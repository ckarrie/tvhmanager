from django.db import models

import tvhapi


class TVHServer(models.Model):
    owner = models.ForeignKey('auth.User')
    name = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField(default=9981)
    username = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    active = models.BooleanField()

    def sync_dvr(self):
        tvhapi.sync_dvr(self)

    def get_current_watching(self):
        tvhapi.get_current_watching(server=self)

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
    uuid = models.CharField(max_length=255, primary=True)
    name = models.CharField(max_length=1000, null=True, blank=True)


class TVHMux(models.Model):
    uuid = models.CharField(max_length=255, primary=True)
    name = models.CharField(max_length=1000, null=True, blank=True)
    network = models.ForeignKey(TVHNetwork)


class TVHService(models.Model):
    mux = models.ForeignKey(TVHMux)
    uuid = models.CharField(max_length=255, primary=True)


class TVHChannel(models.Model):
    service = models.ForeignKey(TVHService)
    uuid = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=1000, null=True, blank=True)

    def __unicode__(self):
        return self.name


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
