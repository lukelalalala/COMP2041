import smtplib, time, inflect
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

fromaddr = <INSERT SENDER>
toaddr = <INSERT RECEIVER>
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
inflectEngine = inflect.engine()

for i in range (1,11):
	msg['Subject'] = inflectEngine.ordinal(i) + " email"
	 
	body = inflectEngine.ordinal(i) + " lol"
	msg.attach(MIMEText(body, 'plain'))
	 
	server = smtplib.SMTP('smtp-mail.outlook.com', 587)
	server.starttls()
	server.login(fromaddr, <INSERT PASSWORD>)
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.quit()
	time.sleep(10)
