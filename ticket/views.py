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
import uuid

def load_connections():
    connections = {}
    
    for station in MetroStation.objects.all() :
        connections[station.station_name]=[]
    for conn in StationConnections.objects.all() :
        if conn.connected_station not in connections[conn.station_name] :
            connections[conn.station_name].append(conn.connected_station)
    return connections
# connections = load_connections()

    

def book_ticket(request):
    system = SystemToggle.objects.first()
    status = system.book_status
    if status == True :
        connections = load_connections()
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
        #print("status=true")
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
            return render(request, 'ticket/ticket_confirmation.html', {
                "origin": origin_station,
                "destination": destination_station,
                "route": route,
                "fare": fare,
                "origin_id": origin_id,
                "destination_id": destination_id,
                "payment_mode": payment_mode
            })
        return render(request, 'ticket/book.html', {'stations': stations, 'username': user_name})
    else:
        return render(request, 'ticket/down.html')
    
def ticket_confirmation(request) :
    if request.method == "POST" :
        user_name = request.user.username
        origin_id = request.POST.get("origin_id")
        destination_id = request.POST.get("destination_id")
        fare = int(request.POST.get("fare"))
        balance = Balance.objects.filter(username=user_name).first().balance
            #print(balance)
        if balance < fare:
            messages.error(request, "Insufficient balance. Please add money to your account.")
            return redirect('add_balance')

        elif balance >= fare:
            balance -= fare
            Balance.objects.filter(username=user_name).update(balance=balance)

            ticket_id = uuid.uuid4().hex[:8]
            otp_org = str(random.randint(100000, 999999))
            time1 = timezone.now()
            #print(ticket_id)
            #print(otp_org)
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
            return redirect('otp_verification', ticket_id=ticket_id)
        return redirect('book_ticket')

def offline_ticket_booking(request) :
    system = SystemToggle.objects.first()
    status = system.book_status
    if status == True :
        stations = MetroStation.objects.all()
        connections = load_connections()
        #print("status=true")
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
                return render(request, 'ticket/offline_confirmation.html', {
                    'origin_station': MetroStation.objects.get(id=origin_id).station_name,
                    'destination_station': MetroStation.objects.get(id=destination_id).station_name,
                    'fare': fare,
                    'ticket_id': ticket_id,
                    'username': user_name
                })

        return render(request, 'ticket/offline_book.html', {'stations': stations, 'username': user_name})
    else:
        return render(request, 'ticket/down.html')

def offline_confirmation(request) :
    return render(request, 'ticket/staff_menu.html')

def add_balance(request):
    system = SystemToggle.objects.first()
    status = system.balance_status
    if status == True :
        if not request.user.is_authenticated:
            return redirect('login')
        user_name = request.user.username
        if request.method == 'POST':
            amount = int(request.POST.get('amount'))
            balance_id = Balance.objects.filter(username=user_name).first() # returns the object if exists else None
            if balance_id:
                balance_id.balance += amount
                balance_id.save()
            else:
                Balance.objects.create(
                    username = user_name,
                    balance = amount
                )
        if Balance.objects.filter(username=user_name).exists():
            current_balance = Balance.objects.get(username=user_name).balance
        else:
            current_balance = 0
        return render(request, 'ticket/balance.html', {'username': user_name,
                                                    'current_balance' : current_balance})
    else :
        return render(request, 'ticket/down.html')

def menu(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'ticket/menu.html')

def ticket_scanner(request):
    system = SystemToggle.objects.first()
    status = system.scan_status
    if status == True :
        stations = MetroStation.objects.all()
        if not request.user.is_authenticated:
            return redirect('login')
        if request.method == 'POST' :
            ticket_id = request.POST.get('ticket_id')
            current_station = request.POST.get('current_station')
            ticket = Database.objects.filter(ticket_id=ticket_id).first()
            if not ticket:
                messages.error(request, "No ticket found")
            if ticket.ticket_status == "Used" :
                messages.error(request, "Ticket already scanned")
            if ticket.origin_scanned == False and ticket.origin_station == current_station :
                ticket.origin_scanned = True
                ticket.ticket_status = "In Use"
                ticket.save()
                messages.success(request, "Ticket scanned successfully")
            if ticket.destination_station == current_station and ticket.destination_scanned == False and ticket.origin_scanned == True :
                ticket.destination_scanned = True
                ticket.ticket_status = "Used"
                ticket.save()
                messages.success(request, "Ticket scanned successfully")
            else : 
                messages.error(request, "Error")
        return render(request, 'ticket/ticket_scanner.html', {'stations':stations})
    else :
        return render(request, 'ticket/down.html')

def view_ticket(request):
    system = SystemToggle.objects.first()
    status = system.view_status
    if status == True :
        if not request.user.is_authenticated :
            return redirect('login')
        user_name = request.user.username
        users = Database.objects.filter(username = user_name).all()
        return render (request, 'ticket/view_ticket.html', {'tickets':users})
    else :
        return render(request, 'ticket/down.html')

def down(request):
    return render('ticket/down.html')

def otp_verification(request, ticket_id):
    otp_record = OTP_Verification.objects.filter(ticket_id=ticket_id).last()
    #print(otp_record)
    if not otp_record:
        messages.error(request, "OTP record not found. Please book ticket again.")
        return redirect('book_ticket')

    if request.method == "POST":
        #print("otp")
        otp_user = request.POST.get('otp_user')
        time2 = timezone.now()
        #print("otp2")
        if time2 > otp_record.time_at_otp_generated + datetime.timedelta(minutes=3):
            print("expired")
            messages.error(request, "OTP Expired")
            return render(request, 'ticket/otp_verification.html', {'ticket_id': ticket_id})

        #print("tried")
        otp_org = otp_record.otp_generate
        if otp_user == otp_org:
            messages.success(request, "Verification Successful")
            #print("success")

            Database.objects.create(
                username=request.user.username,
                origin_station=MetroStation.objects.get(id=otp_record.origin_station_id).station_name,
                destination_station=MetroStation.objects.get(id=otp_record.destination_station_id).station_name,
                fare=otp_record.fare,
                ticket_id=ticket_id,
                timestamp=timezone.now()
            )
            print("success")
            return render(request, 'ticket/confirmation.html', {
                'origin_station': MetroStation.objects.get(id=otp_record.origin_station_id).station_name,
                'destination_station': MetroStation.objects.get(id=otp_record.destination_station_id).station_name,
                'fare': otp_record.fare,
                'ticket_id': ticket_id,
                'username': request.user.username
            })

    return render(request, 'ticket/otp_verification.html', {'ticket_id': ticket_id})





