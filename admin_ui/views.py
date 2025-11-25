from django.shortcuts import render,redirect
from ticket.models import Line,MetroStation,StationConnections,Database,Footfall,SystemToggle
# Create your views here.

def admin_menu(request):
    return render(request,'admin_ui/admin_menu.html')
def line(request):
    lines = Line.objects.all()
    return render(request, "admin_ui/line.html", {"lines": lines})
def add_line(request):
    if request.method == "POST":
        number = request.POST.get("line_number")
        if number:
            Line.objects.create(line_number=number)
        return redirect("line")
    return render(request, "admin_ui/add_line.html")
def delete_line(request, line_id):
    line = Line.objects.get(id=line_id)
    line.delete()
    return redirect("line")

def toggle_line(request, line_id):
    line = Line.objects.get(id=line_id)
    line.is_active = not line.is_active
    line.save()
    return redirect("line")
def metrostation(request):
    stations = MetroStation.objects.all()
    return render(request, "admin_ui/metrostation.html", {"stations": stations})
def add_metrostation(request):
    if request.method == "POST":
        name = request.POST.get("station_name")
        line_id = request.POST.get("line_id")

        if name and line_id:
            line = Line.objects.get(id=line_id)
            MetroStation.objects.create(station_name=name, line=line)

        return redirect("metrostation")

    lines = Line.objects.all()
    return render(request, "admin_ui/add_metrostation.html", {"lines": lines})
def delete_metrostation(request, station_id):
    station = MetroStation.objects.get(id=station_id)
    station.delete()
    return redirect("metrostation")
    
def stationconnections(request):
    connections = StationConnections.objects.all()
    return render(request, "admin_ui/stationconnections.html", {"connections": connections})
def add_connection(request):
    if request.method == "POST":
        station_id = request.POST.get("station_id")
        connected_station_id = request.POST.get("connected_station_id")
        if station_id == connected_station_id:
            return redirect("stationconnections")
        StationConnections.objects.create(
            station=MetroStation.objects.get(id=station_id),
            connected_station=MetroStation.objects.get(id=connected_station_id)
        )
        return redirect("stationconnections")
    stations = MetroStation.objects.all()
    return render(request, "admin_ui/add_connection.html", {"stations": stations})

def view_tickets(request):
    tickets = Database.objects.all()
    return render(request, "admin_ui/tickets.html", {"tickets": tickets})

def system_toggle(request):
    toggle = SystemToggle.objects.first()
    return render(request, "admin_ui/systemtoggle.html", {"toggle": toggle})

def toggle_system(request, field):
    toggle = SystemToggle.objects.first()
    if field == "status":
        toggle.status = not toggle.status
    elif field == "book":
        toggle.book_status = not toggle.book_status
    elif field == "view":
        toggle.view_status = not toggle.view_status
    elif field == "balance":
        toggle.balance_status = not toggle.balance_status
    elif field == "scan":
        toggle.scan_status = not toggle.scan_status
    toggle.save()
    return redirect("system-toggle")

def footfall(request):
    footfalls = Footfall.objects.all()
    return render(request, "admin_ui/footfall.html", {"footfalls": footfalls})
def add_footfall(request):
    if request.method == "POST":
        date = request.POST.get("date")
        station_id = request.POST.get('station_id')
        station = MetroStation.objects.get(id=station_id)
        tickets = Database.objects.filter(timestamp__date=date, ticket_status="Used")
        count = 0

        for ticket in tickets:
            if ticket.origin_station == station:
                count += 1
            if ticket.destination_station == station:
                count += 1
        Footfall.objects.create(
            date=date,
            station=station,
            footfall=count
        )

        return redirect("footfall")
    stations = MetroStation.objects.all()
    return render(request, "admin_ui/add_footfall.html", {"stations": stations})