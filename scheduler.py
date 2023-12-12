#!/usr/bin/python3

def send_emails():
    """
    Sends vaccination reminder emails to parents.

    Retrieves vaccination doses and children's information from storage
    to create notifications for upcoming vaccinations. It then sends
    personalized email reminders to parents using Gmail's SMTP server.

    Notes:
    - Sends reminders based on vaccination dose terms and children's ages.
    - Notifications are appended to the list only if the vaccination dose
      is within two days of the child's required term and hasn't been
      previously notified.
    - Utilizes HTML content in emails to provide clear vaccination details.

    """
    from datetime import datetime
    from email.message import EmailMessage
    from models import storage
    from models.tables import Dose, Child, User
    import os
    import ssl
    import smtplib
    doses = storage.all(Dose).values()
    children = storage.all(Child).values()
    print('children number: ', storage.count(Child))
    notifications = []
    current_date = datetime.now()
    for dose in doses:
        for child in children:
            age_in_days = (current_date - child.birthday).days + 1
            parent = storage.get_by_id(User, child.parent_id)
            # Send the notification at most two days before
            if dose.term == (age_in_days + 2) and dose not in child.doses_notified:
                notifications.append([dose, parent, child, 'in 2 days'])
            elif dose.term == (age_in_days + 1) and dose not in child.doses_notified:
                notifications.append([dose, parent, child, 'for tomorrow'])
            elif dose.term == age_in_days and dose not in child.doses_notified:
                notifications.append([dose, parent, child, 'for today'])
    email_sender = os.getenv('MAIL_USERNAME')
    email_password = os.getenv('MAIL_PASSWORD')
    subject = 'Vaccination reminder'
    print('notifications: ', len(notifications))
    for notificatin in notifications:
        em = EmailMessage()
        em['From'] = email_sender
        em['Subject'] = subject
        html_content = f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        margin: 20px;
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 20px;
                    }}
                    .reminder {{
                        font-size: 16px;
                        margin-bottom: 15px;
                    }}
                    .contact-info {{
                        font-style: italic;
                    }}
                    .signature {{
                        font-weight: bold;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>Hi {notificatin[1].first_name}!</h2>
                    <p>This is a friendly reminder from VaxWise.</p>
                </div>
                <div class="reminder">
                    <p>
                        Just a reminder that your child's
                         {notificatin[2].first_name} {notificatin[0].denomination}
                         vaccination is scheduled {notificatin[3]}.
                         Please ensure your child's timely visit to
                         the medical center.
                    </p>
                </div>
                <div class="contact-info">
                    <p>
                        If you have any questions or need further
                         information about the vaccination, don't
                         hesitate to contact your medical center
                         directly.
                         They can provide the necessary guidance
                         and support:
                    </p>
                </div>
                <div class="signature">
                    <p>Best Regards,<br>VaxWise Team</p>
                </div>
            </body>
        </html>
        """
        email_receiver = notificatin[1].email
        em['To'] = email_receiver
        em.add_alternative(html_content, subtype='html')
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.send_message(em)
            notificatin[2].doses_notified.append(notificatin[0])
            storage.save()
            print('notifications sent')
    storage.close()


if __name__ == '__main__':
    import time
    # Loop to periodically send vaccination reminder emails
    while True:
        # Wait for 60 seconds
        time.sleep(60)
        send_emails()
