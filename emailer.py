"""
Email module which handles the crafting and sending of emails.
"""
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tabulate import tabulate
import smtplib


def send_deals(args, deals):
    headers = [['Title','Link']]
    text = '{table}'
    text = text.format(table=tabulate(headers + deals, headers='firstrow', tablefmt='grid'))
    html = """
        <html>
            <body>
                {table}
            </body>
        </html>
        """
    html = html.format(table=tabulate(
        headers + [('Beautiful Boy', '<a href="{0}" target="_blank">link</a>'.format(r)) for r in deals],
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