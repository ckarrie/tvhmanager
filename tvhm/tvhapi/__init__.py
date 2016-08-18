import datetime

from django.apps import apps
from django.utils import timezone

from tvhm.api import jsonapi
from tvhm.htspapi.tvh.htsp import HTSPClient
import tvhm.htspapi.tvh.log as log

__all__ = ['sync_dvr', 'asyncMetadata']


def sync_dvr(tvhserver):
    TVHChannel = apps.get_model('tvhmanager.TVHChannel')
    TVHRecording = apps.get_model('tvhmanager.TVHRecording')
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

    channel_infos = []


class DummyTVHServer(object):
    host = 'livepl.xn--karri-fsa.de'
    htsp = 9982
    username = ''
    password = ''


def asyncMetadata(tvhserver=None):
    if not tvhserver:
        tvhserver = DummyTVHServer()
    htsp = HTSPClient((tvhserver.host, tvhserver.htsp))
    msg = htsp.hello()
    log.info('connected to %s [%s]' % (msg['servername'], msg['serverversion']))
    log.info('using protocol v%d' % htsp._version)
    cap = []
    if 'servercapability' in msg:
        cap = msg['servercapability']
    log.info('capabilities [%s]' % ','.join(cap))

    # Authenticate
    if tvhserver.username:
        htsp.authenticate(tvhserver.username, tvhserver.password)
        log.info('authenticated as %s' % tvhserver.username)

    # Enable async
    #print htsp.recv()
    #htsp.send('api', {'path': 'status/inputs'})
    #print htsp.recv()
    #htsp.send('api', {'path': 'status/subscriptions'})
    #print htsp.recv()

    return htsp

    args = {}
    # see https://tvheadend.org/projects/tvheadend/wiki/Htsp#enableAsyncMetadata for more args
    # args['epg'] = 1
    # args['lastUpdate'] = 1
    htsp.enableAsyncMetadata(args)
    by_methods = {}

    # results in
    # {'channelAdd': 10098, 'dvrEntryAdd': 1972, 'initialSyncCompleted': 1, 'tagAdd': 37, 'tagUpdate': 37, 'autorecEntryAdd': 81}

    sync_done = False
    while not sync_done:
        try:
            msg = htsp.recv()
        except StopIteration:
            msg = {}
        m = msg.get('method')
        if m:
            if m in by_methods.keys():
                by_methods[m].append(msg)
            else:
                by_methods[m] = [msg]
            if 'initialSyncCompleted' in m:
                sync_done = True

    for k, v in by_methods.items():
        print " - ", k, len(v)

    return htsp

    api_channel_args = {'path': 'channel/list'}
    htsp.send('api', {'path': 'channel/list'})
    msg = htsp.recv()
    print msg

    return by_methods
