import datetime
import random
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail

from auth_system import settings

from .models import MetroStation, OTP_Verification    
from .models import Database
from .models import Balance
from .models import SystemToggle
from .models import StationConnections
from .models import Footfall
import uuid

def load_connections():
    connections = {}
    
    for station in MetroStation.objects.all() :
        connections[station.station_name]=[]
    for conn in StationConnections.objects.all() :
        if conn.connected_station not in connections[conn.station_name] :
            connections[conn.station_name].append(conn.connected_station)
    return connections
connections = load_connections()

    

def book_ticket(request):
    system = SystemToggle.objects.first()
    status = system.book_status
    if status == True :
        toggle = SystemToggle.objects.first()
        toggle_line_1 = toggle.line_1
        toggle_line_2 = toggle.line_2
        toggle_line_3 = toggle.line_3
        toggle_line_4 = toggle.line_4
        if toggle_line_1 == True :
            stations_line_1=MetroStation.objects.filter(line=1)             #returns a Queryset which different from list,dictionary,tuple,set
        else :
            stations_line_1 = MetroStation.objects.none()
        if toggle_line_2 == True :
            stations_line_2=MetroStation.objects.filter(line=2)
        else :
            stations_line_2 = MetroStation.objects.none()          #for querysets use '+' = '|'
        if toggle_line_3 == True :
            stations_line_3=MetroStation.objects.filter(line=3)             #returns a Queryset which different from list,dictionary,tuple,set
        else :
            stations_line_3 = MetroStation.objects.none()
        if toggle_line_4 == True :
            stations_line_4=MetroStation.objects.filter(line=4)
        else :
            stations_line_4 = MetroStation.objects.none() 
        stations = stations_line_1 | stations_line_2 | stations_line_3 | stations_line_4
        

        print("status=true")
        user_name = request.user.username

        if request.method == 'POST':
            origin_id = request.POST.get('origin_station')
            destination_id = request.POST.get('destination_station')
            payment_mode = request.POST.get('payment_mode')

            origin_station = MetroStation.objects.get(id=origin_id).station_name
            destination_station = MetroStation.objects.get(id=destination_id).station_name
            def path_finder(current_station,destination_station,path=[]):
                path = path + [current_station]
                paths = []
                if current_station == destination_station :
                    return path 
                else :
                    for neighbour in connections[current_station] :
                        if neighbour not in path :
                            new_path = path_finder(neighbour,destination_station,path)
                            if new_path :
                                paths.append(new_path)
                if paths :
                    return min(paths,key=len)
            route = path_finder(origin_station,destination_station)
            fare = (len(route)-1) * 10
            ticket_id = uuid.uuid4().hex[:8]
            time_stamp = timezone.now()
            balance = Balance.objects.filter(username=user_name).first().balance
            print(balance)

            if payment_mode == "Cash":
                print("cash")
                Database.objects.create(
                    username=user_name,
                    origin_station=MetroStation.objects.get(id=origin_id).station_name,
                    destination_station=MetroStation.objects.get(id=destination_id).station_name,
                    fare=fare,
                    ticket_id=ticket_id,
                    timestamp=time_stamp,
                    ticket_status="Used",
                    origin_scanned=True,
                    destination_scanned=True
                )
                return render(request, 'ticket/confirmation.html', {
                    'origin_station': MetroStation.objects.get(id=origin_id).station_name,
                    'destination_station': MetroStation.objects.get(id=destination_id).station_name,
                    'fare': fare,
                    'ticket_id': ticket_id,
                    'username': user_name
                })

            else:
                print("UPI")
                if balance < fare:
                    messages.error(request, "Insufficient balance. Please add money to your account.")
                    return redirect('add_balance')

                elif balance >= fare:
                    balance -= fare
                    Balance.objects.filter(username=user_name).update(balance=balance)

                    # Generate OTP and send email
                    otp_org = str(random.randint(100000, 999999))
                    time1 = timezone.now()
                    print(ticket_id)
                    print(otp_org)
                    subject = 'Your Ticket OTP'
                    message = f'Your OTP is {otp_org}. It will expire in 3 minutes.'
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [request.user.email])
                    OTP_Verification.objects.create(
                        ticket_id=ticket_id,
                        otp_generated=otp_org,
                        time_at_otp_generated=time1,
                        origin_station_id=origin_id,
                        destination_station_id=destination_id,
                        fare=fare
                    )

                    # Redirect to OTP verification page
                    return redirect('otp_verification', ticket_id=ticket_id)

        return render(request, 'ticket/book.html', {'stations': stations, 'username': user_name})
    else:
        return render(request, 'ticket/down.html')
    
def footfall():
    obj = Footfall.objects.first()
    date = obj.date
    station = obj.station_name
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
    obj.footfall = count
    obj.save()
