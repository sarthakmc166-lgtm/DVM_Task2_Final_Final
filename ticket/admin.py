from django.contrib import admin
from .models import (
    Database,
    MetroStation,
    Balance,
    Footfall,
    SystemToggle,
    StationConnections,
    OTP_Verification,
    Line
)

@admin.register(Line)
class LineAdmin(admin.ModelAdmin):
    list_display = ('id', 'line_number', 'is_active')
    list_editable = ('line_number', 'is_active')

@admin.register(MetroStation)
class MetroStationAdmin(admin.ModelAdmin):
    list_display = ('id', 'station_name', 'line')

@admin.register(Database)
class DatabaseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'origin_station',
        'destination_station',
        'fare',
        'ticket_id',
        'origin_scanned',
        'destination_scanned',
        'ticket_status',
        'timestamp'
    )
    list_editable = (
        'origin_station',
        'destination_station',
        'fare',
        'ticket_status'
    )

@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'balance')
    list_editable = ('balance',)

@admin.register(Footfall)
class FootfallAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'station', 'footfall')
    list_editable = ('date',)

@admin.register(SystemToggle)
class SystemToggleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'status',
        'book_status',
        'view_status',
        'balance_status',
        'scan_status',
    )
    list_editable = (
        'status',
        'book_status',
        'view_status',
        'balance_status',
        'scan_status',
    )

@admin.register(OTP_Verification)
class OTP_VerificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket_id', 'otp_generated', 'time_at_otp_generated')
    list_editable = ('otp_generated',)

@admin.register(StationConnections)
class StationConnectionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'station', 'connected_station')
    list_editable = ('station', 'connected_station')
