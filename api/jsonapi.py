#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

# Connects django-tvhm with tvheadend

HTTP_GET = 'get'
HTTP_POST = 'post'

API_PATHS = {
    'status': {
        'connections': {
            'c': 'https://github.com/tvheadend/tvheadend/blob/42c9423d8aaf6834ea122c57039d39286eecaae8/'
                 'src/api/api_status.c#L168',
            'path': '/api/status/connections',
            'method': HTTP_GET
        },
        'subscriptions': {
            'c': 'https://github.com/tvheadend/tvheadend/blob/42c9423d8aaf6834ea122c57039d39286eecaae8/'
                 'src/api/api_status.c#L168',
            'path': '/api/status/subscriptions',
            'method': HTTP_GET
        },
        'inputs': {
            'path': '/api/status/inputs',
            'method': HTTP_GET,
        },
        'inputclrstats': {
            'path': '/api/status/inputclrstats',
            'method': HTTP_GET,
            'params': ['uuid']
        },
        'connections/cancel': {
            'path': '/api/connections/cancel',
            'method': HTTP_GET,
            'params': {
                'id': {
                    'formats': [int, list]
                }
            }
        },

    },
    'mpegts': {
        'network_list': {
            'path': '/api/mpegts/input/network_list',
            'params': ['uuid'],

        },
        'network_grid': {
            'path': '/api/mpegts/network/grid',

        },
        'service_grid': {
            'path': '/api/mpegts/service/grid?limit=9999999',
            'params': {
                'limit': {
                    'c': 'https://github.com/tvheadend/tvheadend/blob/42c9423d8aaf6834ea122c57039d39286eecaae8'
                         '/src/api/api_idnode.c#L69'
                },
                'sort': {},
                'dir': {}  # Sort direction
            }
        }
    }
}

# idnode example
# jsonapi.post_data("http://ckarrie:*****@waldmeister:9981/api/idnode/load", payload={'enum': 1, 'class': 'dvrconfig'})


def get_data(url, auth=None, payload={}):
    r = requests.get(url=url, params=payload, auth=auth)
    j = r.json()
    return j


def post_data(url, auth=None, payload={}):
    r = requests.post(url=url, data=payload, auth=auth)
    j = r.json()
    return j


def get_recordings(server, state):
    if state == 'finished':
        path = '/dvrlist_finished'
    elif state == 'upcoming':
        url += '/dvrlist_upcoming'
    elif state == 'failed':
        url += '/dvrlist_failed'

    no_limit = 10000

    recordings = get_data(url, {'limit': no_limit})  # No limit
    return recordings['entries']

def get_networks(url):
    path = "/api/mpegts/network/grid"
    data = {'start': "0", 'limit': "999999999"}
    network_url = url + path
    networks = post_data(network_url, data).get('entries', [])
    #print "networks", len(networks)
    for n in networks:
        node_url = url + '/api/idnode/load'
        node_post_data = {'uuid': n.get('uuid'), 'meta': '1'}
        node_data = post_data(node_url, node_post_data)
        node_dict = node_data['entries'][0]
        n.update({'networkclass': node_dict.get('class')})   

def get_serverinfo(url):
    url += '/api/serverinfo'
        # {"sw_version":"4.1-2140~gf34fac1","api_version":18,"name":"Tvheadend","capabilities":["caclient","tvadapters","satip_client","satip_server","imagecache","timeshift","trace","libav"]}
    return get_data(url)


def get_status_subscriptions(url):
    url += '/api/status/subscriptions'
    subscriptions = get_data(url)
    return subscriptions.get('entries', [])
