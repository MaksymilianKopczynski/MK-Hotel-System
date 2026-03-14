import datetime
from django.db import models
from django.core.exceptions import ValidationError # Imported for throwing validation errors

class Room(models.Model): # using Django to create SQL Table
    number = models.CharField(max_length=10, unique=True) # creating column "number" with unique names
    capacity = models.IntegerField(default=2) # creating column "capacity" 
    description = models.TextField(blank=True) # creating column "description"

    def __str__(self):
        return f"Room {self.number}"

# ContactPerson - the person booking and paying (requires email and phone)
class ContactPerson(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True) # EmailField checks if there is '@' and correct format

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Contact)"

class Reservation(models.Model):
    #Defining available statuses for the reservation using TextChoices
    class Status(models.TextChoices):
        TENTATIVE = 'TENTATIVE', 'Wstępna'
        GUARANTEED = 'GUARANTEED', 'Gwarantowana'
        CANCELLED = 'CANCELLED', 'Anulowana'
        CHECKED_IN = 'CHECKED_IN', 'Zameldowano'
        CHECKED_OUT = 'CHECKED_OUT', 'Wymeldowano'

    reservation_number = models.CharField(max_length=20, unique=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE) 
    contact_person = models.ForeignKey(ContactPerson, on_delete=models.CASCADE) 
    
    # Status column with default value set to GUARANTEED
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.GUARANTEED
    )

    number_of_guests = models.IntegerField(default=1) 
    start_date = models.DateField()
    end_date = models.DateField()
    price_per_night = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Real database column for total price. 
    # blank=True and null=True allow leaving it empty so the system can auto-calculate it
    total_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    def clean(self):
        # Validating dates
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValidationError("End date must be after the start date!")

        # Validating room capacity
        if self.room and self.number_of_guests:
            if self.number_of_guests > self.room.capacity:
                raise ValidationError(f"This room can hold a maximum of {self.room.capacity} guests. Entered: {self.number_of_guests}.")
            if self.number_of_guests < 1:
                raise ValidationError("Reservation must have at least one guest.")

    def save(self, *args, **kwargs):
        # Run validation before saving
        self.full_clean() 

        # Generating reservation number
        if not self.reservation_number:
            current_year = datetime.date.today().year
            last_reservation = Reservation.objects.filter(
                reservation_number__startswith=str(current_year)
            ).order_by('reservation_number').last()

            if last_reservation:
                last_sequence = int(last_reservation.reservation_number[4:])
                new_sequence = last_sequence + 1
            else:
                new_sequence = 1
            self.reservation_number = f"{current_year}{new_sequence:04d}"

        # Auto-calculating total_price ONLY if it's left blank by the user
        if not self.total_price and self.start_date and self.end_date and self.price_per_night:
            nights = (self.end_date - self.start_date).days
            if nights > 0:
                self.total_price = nights * self.price_per_night

        # Executing save function
        super(Reservation, self).save(*args, **kwargs)

    def __str__(self):
        # NEW: Added status to the string representation
        return f"[{self.reservation_number}] {self.contact_person} - {self.room} ({self.get_status_display()})"

# Physical guests assigned to the reservation (Optional to fill)
class Guest(models.Model):
    # Links physical guests to a specific reservation
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name="guests")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    
    # Optional toggle if guest is also the contact person
    is_main_contact = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.first_name} {self.last_name}"