from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(timestamp) + str(user.is_active)
        )

account_activation_token = AccountActivationTokenGenerator()

def send_verification_email(request, user):
    current_site = get_current_site(request)
    subject = 'Activa tu cuenta en ALPHA Project'
    
    context = {
        'user': user,
        'domain': current_site.domain,
        'protocol': settings.PROTOCOL,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'year': timezone.now().year
    }
    
    message = render_to_string('registration/email_verification.html', context)
    
    email = EmailMessage(
        subject,
        message,
        'noreply@alphaproject.com',
        [user.email]
    )
    email.content_subtype = "html"
    email.send()