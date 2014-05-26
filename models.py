import datetime
from django.db import models
from api import jsonapi

from django.utils import timezone


class Server(models.Model):
    name = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField()
    active = models.BooleanField()

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

    def __unicode__(self):
        return self.name


class Channel(models.Model):
    uuid = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=1000, null=True, blank=True)

    def __unicode__(self):
        return self.name


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


