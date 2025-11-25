# from django.db import models


# class Database(models.Model):           #model name should be capitalized
#     username = models.CharField(max_length=100)
#     origin_station = models.CharField(max_length=100)
#     destination_station = models.CharField(max_length=100)
#     fare = models.IntegerField()
#     ticket_id=models.CharField(max_length=100)
#     origin_scanned = models.BooleanField(default=False)
#     destination_scanned = models.BooleanField(default=False)
#     ticket_status = models.CharField(max_length = 100, default="Not Used")
#     timestamp = models.DateTimeField(null=True, blank=True)

# class MetroStation(models.Model):
#     station_name = models.CharField(max_length=100)
#     line = models.IntegerField()
#     station_number = models.IntegerField()

# class StationConnections(models.Model):
#     station_name = models.CharField(max_length=100)
#     connected_station = models.CharField(max_length=100)

# class Balance(models.Model):
#     username = models.CharField(max_length=100)
#     balance = models.IntegerField(default=0)

# class Footfall(models.Model):
#     date = models.DateField(default="2024-01-01")
#     station_name = models.CharField(max_length=100)
#     footfall = models.IntegerField()
#     def foot_fall(self):
#         date = self.date
#         station = self.station_name
#         tickets = Database.objects.filter(timestamp__date=date)
#         count = 0 
#         for ticket in tickets :
#             origin = ticket.origin_station
#             destination = ticket.destination_station
#             if ticket.ticket_status=="Used" :
#                 if station == origin :
#                     count+=1
#                 if station == destination :
#                     count+=1
#         return count
#     def save(self, *args,**kwargs): #*args = extra positional arguments : a tuple
#         self.footfall = self.foot_fall() #*kwargs = extra keyword arguments : a dictionary , while saving , django calls many arguments , these are used to mention all of them
#         return super().save(*args,**kwargs)

# class SystemToggle(models.Model):
#     status = models.BooleanField(default=True)
#     book_status = models.BooleanField(default=True)
#     line_1 = models.BooleanField(default=True)
#     line_2 = models.BooleanField(default=True)
#     line_3 = models.BooleanField(default=True)
#     line_4 = models.BooleanField(default=True)
#     view_status = models.BooleanField(default=True)
#     balance_status = models.BooleanField(default=True)
#     scan_status = models.BooleanField(default=True)

# class OTP_Verification(models.Model):
#     ticket_id = models.CharField(max_length=100)
#     otp_generated = models.CharField(max_length=100)
#     time_at_otp_generated = models.DateTimeField()
#     origin_station_id = models.CharField(max_length=100)
#     destination_station_id = models.CharField(max_length=100)
#     fare = models.IntegerField()



    
from django.db import models
from django.contrib.auth.models import User   

class Line(models.Model):
    line_number = models.IntegerField(unique=True)
    is_active = models.BooleanField(default=True)  # toggle for the line
    def __str__(self):
        return str(self.line_number)

class MetroStation(models.Model):
    station_name = models.CharField(max_length=100)
    line = models.ForeignKey(Line, on_delete=models.CASCADE)
    def __str__(self):
        return self.station_name


class StationConnections(models.Model):
    station = models.ForeignKey(MetroStation, related_name="station_main", on_delete=models.CASCADE)
    connected_station = models.ForeignKey(MetroStation, related_name="station_connected", on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.station} → {self.connected_station}"


class Balance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.user.username} - {self.balance}"


class Database(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    origin_station = models.ForeignKey(MetroStation,  related_name="tickets_origin",on_delete=models.CASCADE)
    destination_station = models.ForeignKey(MetroStation,related_name="tickets_destination", on_delete=models.CASCADE)
    fare = models.IntegerField()
    ticket_id = models.CharField(max_length=100, unique=True)
    origin_scanned = models.BooleanField(default=False)
    destination_scanned = models.BooleanField(default=False)
    ticket_status = models.CharField(max_length=100, default="Not Used")
    timestamp = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.ticket_id


class Footfall(models.Model):
    date = models.DateField(default="2024-01-01")
    station = models.ForeignKey(MetroStation, on_delete=models.CASCADE)
    footfall = models.IntegerField()
    def foot_fall(self):
        tickets = Database.objects.filter(timestamp__date=self.date, ticket_status="Used")
        count = 0
        for ticket in tickets:
            if ticket.origin_station == self.station:
                count += 1
            if ticket.destination_station == self.station:
                count += 1
        return count
    def save(self, *args, **kwargs):
        self.footfall = self.foot_fall()
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.station.station_name} - {self.date}"

class SystemToggle(models.Model):
    status = models.BooleanField(default=True)
    book_status = models.BooleanField(default=True)
    view_status = models.BooleanField(default=True)
    balance_status = models.BooleanField(default=True)
    scan_status = models.BooleanField(default=True)

class OTP_Verification(models.Model):
    ticket_id = models.CharField(max_length=100, unique=True)   # Just a temporary ticket ID
    otp_generated = models.CharField(max_length=6)
    time_at_otp_generated = models.DateTimeField()
    origin_station = models.ForeignKey(MetroStation, related_name="otp_origin", on_delete=models.CASCADE)
    destination_station = models.ForeignKey(MetroStation, related_name="otp_destination", on_delete=models.CASCADE)
    fare = models.IntegerField()
    def __str__(self):
        return f"OTP for {self.ticket_id}"

