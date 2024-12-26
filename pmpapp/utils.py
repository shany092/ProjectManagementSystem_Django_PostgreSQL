from django.core.mail import send_mail
from django.utils.crypto import get_random_string

def send_default_email(recipient_email, password):
    send_mail(
        subject="Welcome!",
        message=f"Your account password: {password}",
        from_email="admin@example.com",
        recipient_list=[recipient_email],
    )