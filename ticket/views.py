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
from .models import Line
import uuid

def load_connections():
    connections = {}
    for station in MetroStation.objects.all():
        connections[station] = []
    for conn in StationConnections.objects.all():
        station = conn.station
        connected_station = conn.connected_station

        if connected_station not in connections[station]:
            connections[station].append(connected_station)

    return connections
# connections = load_connections()

def book_ticket(request):
    system = SystemToggle.objects.first()
    if not system.book_status:
        return render(request, 'ticket/down.html')
    connections = load_connections()
    active_lines = Line.objects.filter(is_active=True)
    stations = MetroStation.objects.filter(line__in=active_lines)
    user_name = request.user.username
    if request.method == 'POST':
        origin_id = request.POST.get('origin_station')
        destination_id = request.POST.get('destination_station')
        payment_mode = request.POST.get('payment_mode')
        origin_station = MetroStation.objects.get(id=origin_id)
        destination_station = MetroStation.objects.get(id=destination_id)

        def path_finder(current_station, destination_station, path=None):
            if path is None:
                path = []
            path = path + [current_station]
            paths = []
            if current_station == destination_station:
                return path
            for neighbour in connections[current_station]:
                if neighbour not in path:
                    new_path = path_finder(neighbour, destination_station, path)
                    if new_path:
                        paths.append(new_path)
            if paths:
                return min(paths, key=len)
        route = path_finder(origin_station, destination_station)
        fare = (len(route) - 1) * 10
        return render(request, 'ticket/ticket_confirmation.html', {
            "origin": origin_station.station_name,
            "destination": destination_station.station_name,
            "route": [s.station_name for s in route],  # list of names for template
            "fare": fare,
            "origin_id": origin_id,
            "destination_id": destination_id,
            "payment_mode": payment_mode
        })
    return render(request, 'ticket/book.html', {
        'stations': stations,
        'username': user_name
    })
    
def ticket_confirmation(request):
    if request.method == "POST":
        user = request.user
        origin_id = request.POST.get("origin_id")
        destination_id = request.POST.get("destination_id")
        fare = int(request.POST.get("fare"))
        origin_station = MetroStation.objects.get(id=origin_id)
        destination_station = MetroStation.objects.get(id=destination_id)
        ticket_id = uuid.uuid4().hex[:8]
        otp_org = str(random.randint(100000, 999999))
        time1 = timezone.now()
        send_mail(
            'Your Ticket OTP',
            f'Your OTP is {otp_org}. It will expire in 3 minutes.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        OTP_Verification.objects.create(
            ticket_id=ticket_id,
            otp_generated=otp_org,
            time_at_otp_generated=time1,
            origin_station=origin_station,
            destination_station=destination_station,
            fare=fare
        )

        return redirect('otp_verification', ticket_id=ticket_id)

    return redirect('book_ticket')

def offline_ticket_booking(request):
    system = SystemToggle.objects.first()
    if not system.book_status:
        return render(request, 'ticket/down.html')
    active_lines = Line.objects.filter(is_active=True)
    stations = MetroStation.objects.filter(line__in=active_lines)
    connections = load_connections()
    user = request.user
    if request.method == 'POST':
        origin_id = request.POST.get('origin_station')
        destination_id = request.POST.get('destination_station')
        payment_mode = request.POST.get('payment_mode')
        origin_station = MetroStation.objects.get(id=origin_id)
        destination_station = MetroStation.objects.get(id=destination_id)
        def path_finder(current_station, destination_station, path=None):
            if path is None:
                path = []
            path = path + [current_station]
            if current_station == destination_station:
                return path
            paths = []
            for neighbor in connections[current_station]:
                if neighbor not in path:
                    new_path = path_finder(neighbor, destination_station, path)
                    if new_path:
                        paths.append(new_path)
            if paths:
                return min(paths, key=len)
        route = path_finder(origin_station, destination_station)
        if not route:
            messages.error(request, "No valid route (active line only).")
            return redirect('offline_ticket_booking')
        fare = (len(route) - 1) * 10
        ticket_id = uuid.uuid4().hex[:8]
        timestamp = timezone.now()
        if payment_mode == "Cash":
            Database.objects.create(
                user=user,
                origin_station=origin_station,
                destination_station=destination_station,
                fare=fare,
                ticket_id=ticket_id,
                timestamp=timestamp,
                ticket_status="Used",        # offline tickets are considered used
                origin_scanned=True,
                destination_scanned=True
            )
            return render(request, 'ticket/offline_confirmation.html', {
                'origin_station': origin_station.station_name,
                'destination_station': destination_station.station_name,
                'fare': fare,
                'ticket_id': ticket_id,
                'username': user.username
            })

    return render(request, 'ticket/offline_book.html', {
        'stations': stations,
        'username': user.username
    })

def offline_confirmation(request) :
    return render(request, 'ticket/staff_menu.html')

def add_balance(request):
    system = SystemToggle.objects.first()
    if not system.balance_status:
        return render(request, 'ticket/down.html')
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user   
    if request.method == 'POST':
        amount = int(request.POST.get('amount'))
        balance_obj = Balance.objects.filter(user=user).first()
        if balance_obj:
            balance_obj.balance += amount
            balance_obj.save()
        else:
            Balance.objects.create(
                user=user,
                balance=amount
            )
    balance_obj = Balance.objects.filter(user=user).first()
    current_balance = balance_obj.balance if balance_obj else 0
    return render(request, 'ticket/balance.html', {
        'username': user.username,
        'current_balance': current_balance
    })


def menu(request):
    if not request.user.is_authenticated:
        return redirect('login')
    username = request.user.username
    return render(request, 'ticket/menu.html',{'username' : username})

def ticket_scanner(request):
    system = SystemToggle.objects.first()
    if not system.scan_status:
        return render(request, 'ticket/down.html')
    stations = MetroStation.objects.all()
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        current_station_id = request.POST.get('current_station')
        current_station = MetroStation.objects.filter(id=current_station_id).first()
        if not current_station:
            messages.error(request, "Invalid station selected.")
            return render(request, 'ticket/ticket_scanner.html', {'stations': stations})
        ticket = Database.objects.filter(ticket_id=ticket_id).first()
        if not ticket:
            messages.error(request, "No ticket found.")
            return render(request, 'ticket/ticket_scanner.html', {'stations': stations})
        if ticket.ticket_status == "Used":
            messages.error(request, "Ticket already used.")
            return render(request, 'ticket/ticket_scanner.html', {'stations': stations})
        if not ticket.origin_scanned and ticket.origin_station == current_station:
            ticket.origin_scanned = True
            ticket.ticket_status = "In Use"
            ticket.save()
            messages.success(request, "Origin station scanned successfully.")
            return render(request, 'ticket/ticket_scanner.html', {'stations': stations})
        if ticket.origin_scanned and not ticket.destination_scanned and ticket.destination_station == current_station:
            ticket.destination_scanned = True
            ticket.ticket_status = "Used"
            ticket.save()
            messages.success(request, "Destination station scanned. Journey completed.")
            return render(request, 'ticket/ticket_scanner.html', {'stations': stations})
        messages.error(request, "Invalid scan attempt.")
        return render(request, 'ticket/ticket_scanner.html', {'stations': stations})
    return render(request, 'ticket/ticket_scanner.html', {'stations': stations})

def view_ticket(request):
    system = SystemToggle.objects.first()
    if not system.view_status:
        return render(request, 'ticket/down.html')
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    tickets = Database.objects.filter(user=user)
    return render(request, 'ticket/view_ticket.html', {
        'tickets': tickets
    })


def down(request):
    return render('ticket/down.html')

def otp_verification(request, ticket_id):
    otp_record = OTP_Verification.objects.filter(ticket_id=ticket_id).last()
    if not otp_record:
        messages.error(request, "OTP record not found. Please book ticket again.")
        return redirect('book_ticket')
    if request.method == "POST":
        otp_user = request.POST.get('otp_user')
        current_time = timezone.now()
        if current_time > otp_record.time_at_otp_generated + datetime.timedelta(minutes=3):
            messages.error(request, "OTP Expired")
            otp_record.delete()   
            return render(request, 'ticket/otp_verification.html', {'ticket_id': ticket_id})
        if otp_user != otp_record.otp_generated:
            messages.error(request, "Incorrect OTP.")
            return render(request, 'ticket/otp_verification.html', {'ticket_id': ticket_id})
        messages.success(request, "Verification Successful")
        user = request.user
        balance_obj = Balance.objects.filter(user=user).first()
        if balance_obj is None:
            messages.error(request, "Balance account not found.")
            return redirect('add_balance')
        if balance_obj.balance < otp_record.fare:
            messages.error(request, "Insufficient balance.")
            return redirect('add_balance')
        balance_obj.balance -= otp_record.fare
        balance_obj.save()
        ticket_obj = Database.objects.create(
            user=user,
            origin_station=otp_record.origin_station,
            destination_station=otp_record.destination_station,
            fare=otp_record.fare,
            ticket_id=ticket_id,
            ticket_status="Not Used",
            timestamp=timezone.now()
        )
        return render(request, 'ticket/confirmation.html', {
            'origin_station': ticket_obj.origin_station.station_name,
            'destination_station': ticket_obj.destination_station.station_name,
            'fare': ticket_obj.fare,
            'ticket_id': ticket_obj.ticket_id,
            'username': user.username
        })

    return render(request, 'ticket/otp_verification.html', {'ticket_id': ticket_id})






