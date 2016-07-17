from twilio.rest import TwilioRestClient
import config
from smtplib import SMTPException, SMTP_SSL
from email.mime.text import MIMEText

class Notifications(object):
    def __init__(self):
        self.twilio_client = TwilioRestClient(config.twilio_account, config.twilio_token)
        self.start_smtp_connection()

    def send_email(self, email_address, subject, message):
        try:
            email = self.build_email(email_address, subject, message)
            self.server.sendmail(config.camper_email, [email_address], email)
        except SMTPException:
            print "Failed to send e-mail to {0}".format(recpient)

    def send_text(self, number, message, url):
        self.twilio_client.messages.create(body=message, to=number, from_=config.twilio_number)
        self.twilio_client.messages.create(body=url, to=number, from_=config.twilio_number)

    def start_smtp_connection(self):
        self.server = SMTP_SSL(host=config.camper_smtp_server, port=config.camper_smtp_port)
        self.server.login(config.camper_email, config.camper_pw)

    def close_smtp_connection(self):
        self.server.quit()

    def build_email(self, recpient, subject, message):
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = config.camper_email
        msg['To'] = recpient
        return msg.as_string()
