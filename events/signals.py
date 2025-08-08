from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from .models import Event, RSVP


@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        try:
            #activation token
            token = default_token_generator.make_token(instance)
            
            activation_url = f"{settings.FRONTEND_URL}/activate/{instance.id}/{token}/"
            
            subject = 'Activate Your Account - Shan Event Management'
            message = f"""Hi {instance.username},

Thank you for registering at Shan Event Management!

Please activate your account by clicking the link below:
{activation_url}

If the link doesn't work, copy and paste it into your browser.

Thank you!
Shan Event Management Team"""

            #send email
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[instance.email],
                fail_silently=False,
            )
            
            print(f'Activation email sent successfully to {instance.email}')
            
        except Exception as e:
            print(f'Failed to send activation email to {instance.email}: {str(e)}')


@receiver(post_save, sender=RSVP)
def send_rsvp_confirmation_email(sender, instance, created, **kwargs):
    """Send confirmation email when RSVP is created or status changes to confirmed"""
    if created or (instance.status == 'confirmed'):
        try:
            user = instance.user
            event = instance.event
            
            if instance.status == 'confirmed':
                # confirmation email
                subject = f'RSVP Confirmation - {event.name}'
                message = f"""Hello {user.first_name or user.username},

You have successfully RSVP'd for the event: '{event.name}'

Event Details:
- Date: {event.date}
- Time: {event.time}
- Location: {event.location}
- Category: {event.category.name}

Your RSVP was confirmed on: {instance.created_at.strftime('%B %d, %Y at %I:%M %p')}

IMPORTANT: You are the exclusive RSVP for this event. Only one person can RSVP per event.

You have also been automatically added as a participant for this event.

We look forward to seeing you at the event!

Best regards,
Shan Event Management Team"""
            
            elif instance.status == 'cancelled':
                subject = f'RSVP Cancellation - {event.name}'
                message = f"""Hello {user.first_name or user.username},

Your RSVP for the event '{event.name}' has been cancelled.

Event Details:
- Date: {event.date}
- Time: {event.time}
- Location: {event.location}

You can still RSVP again if you change your mind before the event date.

Best regards,
Shan Event Management Team"""
            else:
                return

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            print(f'RSVP {instance.status} email sent to {user.email}')
            
        except Exception as e:
            print(f'Failed to send RSVP email: {str(e)}')


@receiver(m2m_changed, sender=Event.rsvps.through)
def send_legacy_rsvp_confirmation_email(sender, instance, action, pk_set, **kwargs):
    """Legacy signal for backward compatibility with old RSVP system"""
    if action == 'post_add':
        try:
            
            user_pk = list(pk_set)[0]
            user = User.objects.get(pk=user_pk)

            if not RSVP.objects.filter(user=user, event=instance).exists():
                subject = f'RSVP Confirmation - {instance.name}'
                message = f"""Hello {user.first_name or user.username},

You have successfully RSVP'd for the event: '{instance.name}'

Event Details:
- Date: {instance.date}
- Time: {instance.time}
- Location: {instance.location}

Thank you for your interest!

Shan Event Management Team"""

                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                
                print(f'Legacy RSVP confirmation email sent to {user.email}')
            
        except Exception as e:
            print(f'Failed to send legacy RSVP confirmation email: {str(e)}')
