import smtplib
from smtplib import SMTPException
from email.message import EmailMessage
import settings

def send_verify_email(recipient, url):
    msg = EmailMessage()
    message = f"Click the following link to verify your email for the CS3103 Image Registry:\n\n{url}\n\nIf you did not make this request, you can ignore this."
    msg.set_content(message)

    msg['Subject'] = 'Image Registry: Verify your email'
    msg['From'] = "imageregistry@cs3103.cs.unb.ca"
    msg['To'] = recipient

    # Send the message via SMTP server
    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(settings.EMAIL_VERIFY_ADDRESS, settings.EMAIL_KEY)
        s.send_message(msg)
        s.quit()
    except SMTPException as e:
        raise Exception({e}) from e