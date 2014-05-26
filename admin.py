from django.contrib import admin

import models


class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'port')
    actions = ['sync_dvr',]

    def sync_dvr(self, request, queryset):
        for server in queryset:
            server.sync_dvr()


class RecordingAdmin(admin.ModelAdmin):
    list_display = ('startdt', 'schedstate', 'title', 'server', 'channel')
    list_filter = ('schedstate', 'server')

admin.site.register(models.Server, ServerAdmin)
admin.site.register(models.Recording, RecordingAdmin)
admin.site.register(models.Channel)
