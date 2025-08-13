from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

from users.models import CustomUser


class Command(BaseCommand):
    help = 'Test email sending functionality (Based on SDT-Django-module-13)'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address to send test to')

    def handle(self, *args, **options):
        test_email = options['email']
        
        
        test_user, created = CustomUser.objects.get_or_create(
            username='test_user',
            defaults={
                'email': test_email,
                'first_name': 'Test',
                'last_name': 'User',
                'is_active': False
            }
        )
        
        if not created:
            test_user.email = test_email
            test_user.is_active = False
            test_user.save()
        
        try:
            token = default_token_generator.make_token(test_user)
            
            activation_url = f"{settings.FRONTEND_URL}/activate/{test_user.id}/{token}/"
            
            subject = 'Test Email - Activate Your Account'
            message = f"""Hi {test_user.username},

This is a test email from Shan Event Management!

Please activate your account by clicking the link below:
{activation_url}

If the link doesn't work, copy and paste it into your browser.

Thank you!
Shan Event Management Team"""

            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[test_email],
                fail_silently=False,
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Test email sent successfully to {test_email}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Activation URL: {activation_url}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to send email: {str(e)}')
            ) 