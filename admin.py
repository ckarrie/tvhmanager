from django.contrib import admin

import models


class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'port')
    actions = ['sync_dvr', 'sync_networks']

    def sync_networks(self, request, queryset):
        for n in queryset:
            n.sync_networks()

    def sync_dvr(self, request, queryset):
        for server in queryset:
            server.sync_dvr()


class RecordingAdmin(admin.ModelAdmin):
    list_display = ('startdt', 'schedstate', 'title', 'server', 'channel')
    list_filter = ('schedstate', 'server')


class NetworkAdmin(admin.ModelAdmin):
    list_display = ('server', 'networkname', 'orbital_pos', 'networkclass', 'autodiscovery', 'skipinitscan', 'idlescan', 'charset')
    list_filter = ('networkclass', 'server')

admin.site.register(models.Server, ServerAdmin)
admin.site.register(models.Recording, RecordingAdmin)
admin.site.register(models.Provider)
admin.site.register(models.Channel)
admin.site.register(models.ChannelTag)
admin.site.register(models.Mux)
admin.site.register(models.Service)
admin.site.register(models.ServiceStream)
admin.site.register(models.EPGSource)
admin.site.register(models.RecordingDescription)
admin.site.register(models.Network, NetworkAdmin)

