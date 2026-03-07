from django.contrib import admin
from .models import AuditLog, AlertConfig, ScheduleConfig

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'dataset', 'score', 'created_at')
    list_filter = ('action',)
    search_fields = ('user__email', 'dataset__name', 'details')
    ordering = ('-created_at',)

@admin.register(AlertConfig)
class AlertConfigAdmin(admin.ModelAdmin):
    list_display = ('dataset', 'threshold', 'is_active', 'updated_at')
    list_filter = ('is_active',)

@admin.register(ScheduleConfig)
class ScheduleConfigAdmin(admin.ModelAdmin):
    list_display = ('dataset', 'frequency', 'is_active', 'last_run_at')
    list_filter = ('frequency', 'is_active')
    ordering = ('-created_at',)
