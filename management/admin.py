from django.contrib import admin
from .models import Room, ContactPerson, Reservation, Guest

# Creating a custom view for Reservations in the Admin Panel
class ReservationAdmin(admin.ModelAdmin):
    # Added 'status' to the visible columns
    list_display = ('reservation_number', 'contact_person', 'room', 'start_date', 'end_date', 'status', 'total_price')
    
    # NEW: Added a sidebar filter for easy sorting by status or start_date
    list_filter = ('status', 'start_date')

admin.site.register(Room)
admin.site.register(ContactPerson)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Guest)