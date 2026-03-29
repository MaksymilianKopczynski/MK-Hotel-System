import json
from django.shortcuts import render
from .models import Room, Reservation

def calendar_view(request):
    rooms = Room.objects.all()
    resources = []
    for room in rooms:
        resources.append({
            'id': str(room.id),
            'title': f"Pokój {room.number} ({room.capacity} os.)"
        })

    reservations = Reservation.objects.exclude(status='CANCELLED')
    events = []
    for res in reservations:
        bg_color = '#007bff'
        if res.status == 'TENTATIVE':
            bg_color = '#ffc107'
        elif res.status == 'GUARANTEED':
            bg_color = '#28a745'
        elif res.status == 'CHECKED_IN':
            bg_color = '#17a2b8'
        elif res.status == 'CHECKED_OUT':
            bg_color = '#6c757d'

        events.append({
            'id': str(res.id),
            'resourceId': str(res.room.id),
            'title': f"{res.contact_person.first_name} {res.contact_person.last_name}",
            
            # MAGIA: Doklejamy godzinę 14:00 do daty startu i 12:00 do daty końca (format ISO 8601)
            'start': res.start_date.strftime('%Y-%m-%d') + 'T14:00:00',
            'end': res.end_date.strftime('%Y-%m-%d') + 'T12:00:00',
            
            # Mówimy kalendarzowi, że to nie jest rezerwacja "całodniowa"
            'allDay': False, 
            
            'backgroundColor': bg_color,
        })

    context = {
        'resources_json': json.dumps(resources),
        'events_json': json.dumps(events)
    }
    
    return render(request, 'management/calendar.html', context)