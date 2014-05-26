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