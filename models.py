import datetime
from django.db import models
from api import jsonapi

from django.utils import timezone


class Server(models.Model):
    name = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField(default=9981)
    username = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    active = models.BooleanField(default=True)

    def sync_networks(self):
        url = 'http://%s:%s' % (self.host, self.port)
        networks = jsonapi.get_networks(url=url)
        n_fields = [f.name for f in Network._meta.fields]
        for n in networks:
            try:
                nw = Network.objects.get(uuid=n.get('uuid'), server=self)
            except Network.DoesNotExist:
                nw = Network(uuid=n.get('uuid'), server=self)
            for k, v in n.items():
                if k in n_fields:
                    setattr(nw, k, v)
            nw.save()


    def sync_dvr(self):
        url = 'http://%s:%s' % (self.host, self.port)
        dvr_finished = jsonapi.get_recordings(url=url, state='finished')
        dvr_failed = jsonapi.get_recordings(url=url, state='failed')
        dvr_upcoming = jsonapi.get_recordings(url=url, state='upcoming')

        all_recordings = dvr_finished + dvr_failed + dvr_upcoming
        qs = []
        tz = timezone.get_current_timezone()
        for rec in all_recordings:
            uuid = rec.get('id', 'noid')
            channel, c = Channel.objects.get_or_create(uuid=rec.get('channelid'), defaults={'name': rec.get('channel', 'No Channel Name')})
            rec_data = {
                'status': rec.get('status', 'No Status'),
                'schedstate': rec.get('schedstate', 'No Schedule state'),
                'startdt': timezone.make_aware(datetime.datetime.fromtimestamp(rec.get('start', 0)), timezone=tz),
                'enddt': timezone.make_aware(datetime.datetime.fromtimestamp(rec.get('end', 0)), timezone=tz),
                'title': rec.get('title', 'No Title'),
                'channel': channel
            }

            r, c = Recording.objects.get_or_create(uuid=uuid, server=self, defaults=rec_data)
            if not c:
                for k, v in rec_data.items():
                    setattr(r, k, v)
                r.save()

            qs.append(r)

        return qs

    def sync_channels(self):
        pass

    def __unicode__(self):
        return self.name


class Network(models.Model):
    server = models.ForeignKey(Server)
    uuid = models.CharField(max_length=255, unique=True)
    networkname = models.CharField(max_length=255)
    orbital_pos = models.CharField(max_length=10)
    nid = models.IntegerField(default=0)
    autodiscovery = models.BooleanField(default=True)
    skipinitscan = models.BooleanField(default=True)
    idlescan = models.BooleanField(default=False)
    sid_chnum = models.BooleanField(default=False)
    satip_source = models.IntegerField(default=0)
    charset = models.CharField(max_length=255, null=True, blank=True)
    localtime = models.BooleanField(default=False)
    networkclass = models.CharField(max_length=255, choices=(
        ('dvb_network_dvbs', 'DVB Sat'),
    ))

    def __unicode__(self):
        return self.networkname

class Provider(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Mux(models.Model):
    network = models.ForeignKey(Network)
    enabled = models.BooleanField(default=True)
    uuid = models.CharField(max_length=255, unique=True)
    delsys = models.CharField(max_length=255, choices=(
        ('DVBS', 'DVB-S'),
    ))
    frequency = models.IntegerField(null=True, blank=True)
    symbolrate = models.IntegerField(null=True, blank=True)
    polarisation = models.CharField(max_length=10, null=True, blank=True, choices=(
        ('H', 'horizontal'),
        ('V', 'vertical')
    ))
    modulation = models.CharField(max_length=10, null=True, blank=True, choices=(
        ('QPSK', 'QPSK'),
    ))
    fec = models.CharField(max_length=10, null=True, blank=True, choices=(
        ('3/4', '3/4'),
    ))
    rolloff = models.IntegerField(null=True, blank=True)
    pilot = models.CharField(max_length=10, null=True, blank=True, choices=(
        ('AUTO', 'Auto (depends on tuner settings)'),
    ))
    stream_id = models.IntegerField(null=True, blank=True)
    pls_mode = models.CharField(max_length=10, null=True, blank=True, choices=(
        ('ROOT', 'Root'),
        ('GOLD', 'Gold'),
        ('COMBO', 'Combo'),
    ))
    pls_code = models.IntegerField(null=True, blank=True)
    epg = models.IntegerField(null=True, blank=True)
    onid = models.IntegerField(verbose_name='Original Network ID', null=True, blank=True)
    tsid = models.IntegerField(verbose_name='Transport Stream ID', null=True, blank=True)
    scan_result = models.IntegerField(null=True, blank=True, choices=(
        # see /src/input/mpegts.h
        (0, 'None'),
        (1, 'Scan OK'),
        (2, 'Scan failed')
    ))
    ac3_detection = models.IntegerField(null=True, blank=True, choices=(
        (0, 'Standard'),
        (1, 'AC3 = descriptor 6'),
        (2, 'Ignore descriptor 5')
    )) # pmt_06_ac3


class Service(models.Model):
    mux = models.ForeignKey(Mux)
    uuid = models.CharField(max_length=255, unique=True)
    enabled = models.BooleanField(default=True)
    sid = models.IntegerField(verbose_name='Service ID')
    lcn = models.IntegerField(default=0)
    lcn_minor = models.IntegerField(default=0)
    lcn2 = models.IntegerField(default=0)
    svcname = models.CharField(max_length=500, verbose_name='Service Name')
    provider = models.ForeignKey(Provider, null=True, blank=True)
    dvb_servicetype = models.IntegerField(default=0)
    dvb_ignore_eit = models.BooleanField(default=False)
    prefcapid = models.IntegerField(default=0)
    prefcapid_lock = models.IntegerField(default=0)
    force_caid = models.IntegerField(default=0)
    created_at = models.DateTimeField()
    last_seen = models.DateTimeField()
    auto = models.IntegerField(default=0)
    priority = models.IntegerField(default=0)
    pcr = models.IntegerField(default=0)
    pmt = models.IntegerField(default=0)

    def __unicode__(self):
        if self.svcname:
            return self.svcname
        return "{%s}" % self.uuid


class ServiceStream(models.Model):
    service = models.ForeignKey(Service)
    pid = models.IntegerField(default=0)
    streamtype = models.CharField(max_length=255, choices=(
        ('MPEG2VIDEO', 'MPEG2 Video'),
        ('MPEG2AUDIO', 'MPEG2 Audio'),
        ('AC3', 'AC3 Audio'),
        ('TELETEXT', 'Teletext'),
    ))
    position = models.IntegerField(default=0)
    width = models.IntegerField(null=True, blank=True)
    height =  models.IntegerField(null=True, blank=True)
    duration =  models.IntegerField(null=True, blank=True)
    language = models.CharField(max_length=10, null=True, blank=True)
    audio_type = models.IntegerField(default=0)
    


class EPGSource(models.Model):
    epgid = models.CharField(max_length=255, choices=(
        ('eit', 'EPG DVB Table'),
        ('uk_freesat', 'UK Freesat'),
        ('uk_freeview', 'UK Freeview'),
        ('viasat_baltic', 'viasat_baltic'),
        ('opentv-ausat', 'opentv-ausat'),
        ('opentv-skyit', 'opentv-skyit')
    ))
    services = models.ManyToManyField(Service, null=True, blank=True, symmetrical=False)

class ChannelTag(models.Model):
    uuid = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=1000, null=True, blank=True)
    enabled = models.BooleanField(default=True)
    sort_index = models.IntegerField(default=0)
    internal = models.BooleanField(default=False)
    private = models.BooleanField(default=False)
    icon_url = models.CharField(max_length=500, null=True, blank=True)
    icon_has_title = models.BooleanField(default=False)
    comment = models.CharField(max_length=500)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('sort_index', 'name')


class Channel(models.Model):
    uuid = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=1000, null=True, blank=True)
    enabled = models.BooleanField(default=True)
    number = models.IntegerField(default=0)
    user_icon_url = models.CharField(max_length=500, null=True, blank=True)
    auto_epg_channel = models.BooleanField(default=True)
    epg_source = models.ForeignKey(EPGSource, null=True, blank=True)
    services = models.ManyToManyField(Service, null=True, blank=True)
    channeltags = models.ManyToManyField(ChannelTag, null=True, blank=True)
    dvr_pre = models.IntegerField(default=0)
    dvr_post = models.IntegerField(default=0)
    icon_url = models.CharField(max_length=500, null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Recording(models.Model):
    server = models.ForeignKey(Server)
    uuid = models.CharField(max_length=255)
    channel = models.ForeignKey(Channel)
    title = models.CharField(max_length=1000)
    startdt = models.DateTimeField()
    enddt = models.DateTimeField()
    url = models.CharField(max_length=1000, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255)
    schedstate = models.CharField(max_length=255)



class RecordingDescription(models.Model):
    recording = models.ForeignKey(Recording)
    lang_code = models.CharField(max_length=255)
    description = models.TextField()


