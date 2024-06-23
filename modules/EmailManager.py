import smtplib, random
from hashlib import sha512
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

class EmailManager:
    def __init__(self, host, port, sender_email, sender_password):
        self.sender = sender_email
        self.password = sender_password
        self.host = host
        self.port = port
    
    def __generateOTP(self):
        return random.randint(000000, 999999)
    
    def __encryptOTP(self, otp):
        return sha512(str(otp).encode('utf-8')).hexdigest()
    
    def sendEmailVerificationOTP(self, targetEmail):
        otp = self.__generateOTP()
        encryptedOTP = self.__encryptOTP(otp)
        subject = "Your OTP for Verification in Money Wealth Management"
        body = f"""
Your one time password for logging in Money Wealth Management - Stock Trading | Stock Tips is {otp}

Please do not reply to this message. This OTP is for login purposes only. Do not share this OTP with anyone if you are not trying to log in.
"""
        resp=self.sendEmail([targetEmail],subject,body,False)
        if resp:
            return [True, encryptedOTP]
        return [False, None]
    
    def sendEmail(self, recipients, subject, body, attachment_path=None):
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        if attachment_path:
            filename = os.path.basename(attachment_path)
            attachment = open(attachment_path, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {filename}")
            msg.attach(part)
        try:
            server = smtplib.SMTP(self.host, self.port)
            server.starttls()
            server.login(self.sender, self.password)
            text = msg.as_string()
            server.sendmail(self.sender, recipients, text)
            server.quit()
            print(f"Email sent successfully to {', '.join(recipients)}")
            return True
        except Exception as e:
            print(f"Failed to send email. Error: {str(e)}")
            return False