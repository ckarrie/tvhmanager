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

admin.site.register(models.TVHServer, ServerAdmin)
admin.site.register(models.TVHRecording, RecordingAdmin)
#admin.site.register(models.TVHProvider)
admin.site.register(models.TVHChannel)
admin.site.register(models.TVHChannelTag)
admin.site.register(models.TVHMux)
admin.site.register(models.TVHService)
#admin.site.register(models.ServiceStream)
admin.site.register(models.TVHEPGSource)
admin.site.register(models.TVHRecordingDescription)
admin.site.register(models.TVHNetwork, NetworkAdmin)

