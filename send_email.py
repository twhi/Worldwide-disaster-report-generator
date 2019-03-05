# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

# Open a plain text file for reading.  For this example, assume that
# the text file contains only ASCII characters.

# Create a text/plain message
msg = MIMEText("hello there mate")

# me == the sender's email address
# you == the recipient's email address
msg['Subject'] = 'The subject'
msg['From'] = 'geog.hackday@gmail.com'
msg['To'] = 'tom.whitehead@oup.com'

# Send the message via our own SMTP server, but don't include the
# envelope header.
s = smtplib.SMTP('localhost')
s.sendmail('geog.hackday@gmail.com', ['tom.whitehead@oup.com'], msg.as_string())
s.quit()