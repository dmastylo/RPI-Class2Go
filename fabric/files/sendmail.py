# settings

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587


# now construct the message
import smtplib, email
from email import encoders
import os
import argparse
from email.MIMEImage import MIMEImage

parser = argparse.ArgumentParser(description='Send an attachment via gmail')
parser.add_argument('-u','--username', dest='smtp_username', help='SMTP Username')
parser.add_argument('-p','--password', dest='smtp_password', help='SMTP Password')
parser.add_argument('-f','--from', dest='smtp_from', help='SMTP From Address')
parser.add_argument('-t', '--to', dest='smtp_to', help='SMTP To Address')
parser.add_argument('-a', '--attachment', dest='smtp_attachment', help='File to send')
parser.add_argument('-s', '--subject', dest='smtp_subject', help='Subject of Message')
parser.add_argument('-m', '--message', dest='smtp_message', help='Body of Message')


args = parser.parse_args()


msg = email.MIMEMultipart.MIMEMultipart()
body = email.MIMEText.MIMEText(args.smtp_message)

fp = open(args.smtp_attachment, 'rb')
attachment = MIMEImage(fp.read())
fp.close()
attachment.add_header('Content-ID', args.smtp_attachment)
# attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(args.smtp_attachment))
# encoders.encode_base64(attachment)

# msg.attach(args.smtp_message)
msg.attach(attachment)
msg.add_header('From',args.smtp_from)
msg.add_header('To', args.smtp_to)
msg.add_header('Subject', args.smtp_subject)

# now send the message
mailer = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
# EDIT: mailer is already connected
# mailer.connect()
mailer.ehlo()
mailer.starttls()
mailer.ehlo
mailer.login(args.smtp_username, args.smtp_password)

mailer.sendmail(args.smtp_from, [args.smtp_to], msg.as_string())
mailer.quit()
