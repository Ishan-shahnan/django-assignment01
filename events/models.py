from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='event_images/', default='event_images/default.jpg')
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')
    rsvps = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='rsvp_events', blank=True)

    def __str__(self):
        return self.name

    @property
    def is_past(self):
        return timezone.now() > timezone.make_aware(timezone.datetime.combine(self.date, self.time))
    
    @property
    def rsvp_count(self):
        """Get the count of RSVPs for this event"""
        return self.event_rsvps.filter(status='confirmed').count()
    
    @property
    def rsvp_users(self):
        """Get all users who have RSVP'd to this event"""
        return settings.AUTH_USER_MODEL.objects.filter(user_rsvps__event=self, user_rsvps__status='confirmed')

    @property
    def has_confirmed_rsvp(self):
        """Check if this event has a confirmed RSVP"""
        return self.event_rsvps.filter(status='confirmed').exists()
    
    @property
    def confirmed_rsvp_user(self):
        """Get the user who has confirmed RSVP for this event"""
        confirmed_rsvp = self.event_rsvps.filter(status='confirmed').first()
        return confirmed_rsvp.user if confirmed_rsvp else None


class RSVP(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_rsvps')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_rsvps')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, help_text="Optional notes from the participant")
    
    class Meta:
        unique_together = ('user', 'event') 
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.event.name} ({self.status})"
    
    def clean(self):
        """Validate that user cannot RSVP to past events and only one RSVP per event"""
        if self.event and self.event.is_past:
            raise ValidationError("Cannot RSVP to past events.")
        
        # checks already rvp
        if self.status == 'confirmed':
            existing_confirmed = RSVP.objects.filter(
                event=self.event, 
                status='confirmed'
            ).exclude(id=self.id).first()
            
            if existing_confirmed:
                raise ValidationError("This event already has a confirmed RSVP. Only one person can RSVP per event.")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Participant(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    events = models.ManyToManyField(Event, related_name='participants')

    def __str__(self):
        return self.name
