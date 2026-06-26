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
            'start': res.start_date.strftime('%Y-%m-%d') + 'T14:00:00',
            'end': res.end_date.strftime('%Y-%m-%d') + 'T12:00:00',
            'allDay': False, 
            'backgroundColor': bg_color,

            # PASSING EXTENDED PROPS TO THE FRONTEND MODAL
            'extendedProps': {
                # Using get_status_display() to show Polish labels (e.g., 'Gwarantowana')
                'status': res.get_status_display(), 
                'guest_name': f"{res.contact_person.first_name} {res.contact_person.last_name}",
                'check_in': res.start_date.strftime('%Y-%m-%d'),
                'check_out': res.end_date.strftime('%Y-%m-%d'),
                
                # Using the exact field name from models.py
                'reservation_number': str(res.reservation_number)
            }

        })

    context = {
        'resources_json': json.dumps(resources),
        'events_json': json.dumps(events)
    }
    
    return render(request, 'management/calendar.html', context)