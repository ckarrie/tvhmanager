import datetime
from django.db import models
from api import jsonapi

import tvhapi


class TVHServer(models.Model):
    owner = models.ForeignKey('auth.User')
    name = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField(default=9981)
    htsp = models.PositiveIntegerField(default=9982)
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
        tvhapi.sync_dvr(self)

    def get_current_watching(self):
        return tvhapi.get_current_watching(tvhserver=self)

    def base_url(self):
        d = {
            'username': self.username, 'password': self.password,
            'host': self.host, 'port': self.port
        }
        return 'http://%(username)s:%(password)s@%(host)s:%(port)d' % d

    def __unicode__(self):
        return self.name


class TVHNetwork(models.Model):
    server = models.ForeignKey(TVHServer)
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


class TVHMux(models.Model):
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


class TVHService(models.Model):
    mux = models.ForeignKey(TVHMux)
    uuid = models.CharField(max_length=255, unique=True)


class TVHEPGSource(models.Model):
    uuid = models.UUIDField()


class TVHChannelTag(models.Model):
    uuid = models.UUIDField()


class TVHChannel(models.Model):
    uuid = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=1000, null=True, blank=True)
    enabled = models.BooleanField(default=True)
    number = models.IntegerField(default=0)
    user_icon_url = models.CharField(max_length=500, null=True, blank=True)
    auto_epg_channel = models.BooleanField(default=True)
    epg_source = models.ForeignKey(TVHEPGSource, null=True, blank=True)
    services = models.ManyToManyField(TVHService, blank=False)
    channeltags = models.ManyToManyField(TVHChannelTag, blank=True)
    dvr_pre = models.IntegerField(default=0)
    dvr_post = models.IntegerField(default=0)
    icon_url = models.CharField(max_length=500, null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class TVHRecording(models.Model):
    server = models.ForeignKey(TVHServer)
    uuid = models.CharField(max_length=255)
    channel = models.ForeignKey(TVHChannel)
    title = models.CharField(max_length=1000)
    startdt = models.DateTimeField()
    enddt = models.DateTimeField()
    url = models.CharField(max_length=1000, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255)
    schedstate = models.CharField(max_length=255)


class TVHRecordingDescription(models.Model):
    recording = models.ForeignKey(TVHRecording)
    lang_code = models.CharField(max_length=255)
    description = models.TextField()


class ChannelSet(models.Model):
    owner = models.ForeignKey('auth.User')
    name = models.CharField(max_length=100)
