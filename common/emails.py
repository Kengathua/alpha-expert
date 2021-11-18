"""Background email sending task."""
from celery import shared_task
from core import settings
from django.core.mail import EmailMultiAlternatives


@shared_task(name=__name__ + '.send_email', ignore_result=True)
def send_email(
        subject='', plain_text='', html_message='', recipients=None,
        attachments=None, bcc=None, cc=None):
    """Send an email, using default Django email settings."""
    from_email = settings.OUTGOING_EMAIL_SOURCE
    alternatives = None
    if html_message:
        alternatives = [(html_message, 'text/html')]
    cc = cc or []
    cc.append('gathua.karanja5@students.ku.ac.ke')
    mail = EmailMultiAlternatives(
        subject=subject, body=plain_text, from_email=from_email, to=recipients,
        bcc=bcc, cc=cc, alternatives=alternatives)
    # fail_silently is False by default
    if attachments:
        filename, content, mimetype = attachments[0]
        mail.attach(filename, content, mimetype)
    return mail.send()
