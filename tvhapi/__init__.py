import datetime

from django.apps import apps
from django.utils import timezone

from api import jsonapi

__all__ = ['sync_dvr',]

TVHChannel = apps.get_model('tvhmanager.TVHChannel')
TVHRecording = apps.get_model('tvhmanager.TVHRecording')


def sync_dvr(tvhserver):
    url = tvhserver.base_url()
    dvr_finished = jsonapi.get_recordings(url=url, state='finished')
    dvr_failed = jsonapi.get_recordings(url=url, state='failed')
    dvr_upcoming = jsonapi.get_recordings(url=url, state='upcoming')

    all_recordings = dvr_finished + dvr_failed + dvr_upcoming
    qs = []
    tz = timezone.get_current_timezone()
    for rec in all_recordings:
        uuid = rec.get('id', 'noid')
        channel, c = TVHChannel.objects.get_or_create(uuid=rec.get('channelid'),
                                                      defaults={'name': rec.get('channel', 'No Channel Name')})
        rec_data = {
            'status': rec.get('status', 'No Status'),
            'schedstate': rec.get('schedstate', 'No Schedule state'),
            'startdt': timezone.make_aware(datetime.datetime.fromtimestamp(rec.get('start', 0)), timezone=tz),
            'enddt': timezone.make_aware(datetime.datetime.fromtimestamp(rec.get('end', 0)), timezone=tz),
            'title': rec.get('title', 'No Title'),
            'channel': channel
        }

        r, c = TVHRecording.objects.get_or_create(uuid=uuid, server=tvhserver, defaults=rec_data)
        if not c:
            for k, v in rec_data.items():
                setattr(r, k, v)
            r.save()

        qs.append(r)

    return qs


def get_current_watching(tvhserver):
    subscriptions = jsonapi.get_status_subscriptions(url=tvhserver.base_url())
    channels = []
    for sub in subscriptions:
        channel_name = sub.get('channel', None)
        service = sub.get('service', None)
        if channel_name and service and channel_name not in channels:
            channels.append(
                (channel_name, service)
            )

    channel_infos =
