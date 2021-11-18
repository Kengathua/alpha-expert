from django.core.mail import EmailMessage

import smtplib

def send_email(current_price, signal):
    body=current_price, signal
    # email = EmailMessage('Subject', body, to=['gathuakennedy@gmail.com'])
    # email.send()

    server = smtplib.SMTP_SSL('smtp.googlemail.com', 465)
    server.login('alphaexperts245@gmail.com', 'alphaexperts254')
    server.sendmail('alphaexperts245@gmail.com',
                    'gathuakennedy@gmail.com', body)
