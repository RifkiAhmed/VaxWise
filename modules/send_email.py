#!/usr/bin/python3

def send_email(subject, html_content, receiver):
    """Sends emails to users.

    Args:
    - subject: Subject line for the email.
    - html_content: HTML content of the email.
    - receiver: Email address of the receiver.

    Note:
    - Requires 'MAIL_USERNAME' and 'MAIL_PASSWORD' environment variables for sender authentication.
    """
    from email.message import EmailMessage
    import os
    import smtplib
    import ssl

    sender = os.getenv('MAIL_USERNAME')
    password = os.getenv('MAIL_PASSWORD')

    email = EmailMessage()
    email['From'] = sender
    email['Subject'] = subject
    email['To'] = receiver
    email.add_alternative(html_content, subtype='html')

    context = ssl.create_default_context()

    host = 'smtp.gmail.com'
    port = 465

    with smtplib.SMTP_SSL(host, port, context=context) as smtp:
        smtp.login(sender, password)
        smtp.send_message(email)
