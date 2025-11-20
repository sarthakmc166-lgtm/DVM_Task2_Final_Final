from django.contrib import admin
from .models import Database
from .models import MetroStation
from .models import Balance
from .models import Footfall
from .models import SystemToggle
from .models import StationConnections
from .models import OTP_Verification

@admin.register(MetroStation)
class MetroStationAdmin(admin.ModelAdmin):
    list_display = ('id','station_name', 'line', 'station_number')
    list_editable = ('station_name', 'line', 'station_number')

@admin.register(Database)
class DatabaseAdmin(admin.ModelAdmin):
    list_display = ('id','username', 'origin_station', 'destination_station', 'fare', 'ticket_id', 'origin_scanned', 'destination_scanned', 'ticket_status', 'timestamp')
    list_editable = ('username', 'origin_station', 'destination_station', 'fare', 'ticket_id', 'origin_scanned', 'destination_scanned', 'ticket_status', 'timestamp')

@admin.register(Balance)
class BalanceAdmmin(admin.ModelAdmin):
    list_display = ('id','username', 'balance')
    list_editable = ('username', 'balance')

@admin.register(Footfall)
class FootfallAdmin(admin.ModelAdmin) :
    list_display = ('id','date','station_name', 'footfall')
    list_editable = ('date','station_name')

@admin.register(SystemToggle)
class SystemToggleAdmin(admin.ModelAdmin):
    list_display = ('id','status','book_status', 'view_status', 'balance_status', 'scan_status', 'line_1','line_2','line_3','line_4',)
    list_editable = ('status','book_status', 'view_status', 'balance_status', 'scan_status','line_1','line_2','line_3','line_4',)

@admin.register(OTP_Verification)
class OTP_VerificationAdmin(admin.ModelAdmin):
    list_display = ('ticket_id','otp_generated')

@admin.register(StationConnections)
class StationConnectionsAdmin(admin.ModelAdmin):
    list_display = ('id','station_name','connected_station')
    list_editable = ('station_name','connected_station')