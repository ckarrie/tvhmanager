#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

# Connects django-tvhm with tvheadend


def get_data(url, payload={}):
    r = requests.get(url=url, params=payload)
    j = r.json()
    return j


def post_data(url, payload={}):
    r = requests.post(url=url, data=payload)
    j = r.json()
    return j


def get_recordings(url, state):
    if state == 'finished':
        url += '/dvrlist_finished'
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

    return networks
