"""
Email module which handles the crafting and sending of emails.
"""
import config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tabulate import tabulate
import smtplib


def send_deals(args, events):
    headers = [['Title','Link']]
    text = '{table}'
    text = text.format(table=tabulate(headers + events, headers='firstrow', tablefmt='grid'))
    html = """
        <html>
            <body>
                {table}
            </body>
        </html>
        """
    html = html.format(table=tabulate(
        headers + [(event.title, '<a href="{0}" target="_blank">link</a>'.format(event.link)) for event in events],
        headers='firstrow',
        tablefmt='html')
    )

    message = MIMEMultipart('alternative', None, [MIMEText(text), MIMEText(html, 'html')])
    message['Subject'] = 'TIFF TICKET ALERT'
    message['From'] = 'allenqdam@gmail.com'
    message['To'] = 'allenqdam@gmail.com'

    server = smtplib.SMTP_SSL('smtp.gmail.com')
    server.login(args.user, args.password)
    server.send_message(message)
    server.quit()

    print('Ticket alert sent!')