from django.db import models


class Database(models.Model):           #model name should be capitalized
    username = models.CharField(max_length=100)
    origin_station = models.CharField(max_length=100)
    destination_station = models.CharField(max_length=100)
    fare = models.IntegerField()
    ticket_id=models.CharField(max_length=100)
    origin_scanned = models.BooleanField(default=False)
    destination_scanned = models.BooleanField(default=False)
    ticket_status = models.CharField(max_length = 100, default="Not Used")
    timestamp = models.DateTimeField(null=True, blank=True)

class MetroStation(models.Model):
    station_name = models.CharField(max_length=100)
    line = models.IntegerField()
    station_number = models.IntegerField()

class StationConnections(models.Model):
    station_name = models.CharField(max_length=100)
    connected_station = models.CharField(max_length=100)

class Balance(models.Model):
    username = models.CharField(max_length=100)
    balance = models.IntegerField(default=0)

class Footfall(models.Model):
    date = models.DateField(default="2024-01-01")
    station_name = models.CharField(max_length=100)
    footfall = models.IntegerField()
    def foot_fall(self):
        date = self.date
        station = self.station_name
        tickets = Database.objects.filter(timestamp__date=date)
        count = 0 
        for ticket in tickets :
            origin = ticket.origin_station
            destination = ticket.destination_station
            if ticket.ticket_status=="Used" :
                if station == origin :
                    count+=1
                if station == destination :
                    count+=1
        return count
    def save(self, *args,**kwargs):
        self.footfall = self.foot_fall()
        return super().save(*args,**kwargs)

class SystemToggle(models.Model):
    status = models.BooleanField(default=True)
    book_status = models.BooleanField(default=True)
    line_1 = models.BooleanField(default=True)
    line_2 = models.BooleanField(default=True)
    line_3 = models.BooleanField(default=True)
    line_4 = models.BooleanField(default=True)
    view_status = models.BooleanField(default=True)
    balance_status = models.BooleanField(default=True)
    scan_status = models.BooleanField(default=True)

class OTP_Verification(models.Model):
    ticket_id = models.CharField(max_length=100)
    otp_generated = models.CharField(max_length=100)
    time_at_otp_generated = models.DateTimeField()
    origin_station_id = models.CharField(max_length=100)
    destination_station_id = models.CharField(max_length=100)
    fare = models.IntegerField()



    
