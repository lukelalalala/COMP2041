# A python script that sends email reminder when enrolment for a UNSW course is available
import requests, time, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

page = requests.get("http://timetable.unsw.edu.au/2018/COMP4920.html")

def email():
	fromaddr = <INSERT EMAIL>
	toaddr = <INSERT EMAIL>
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = "check 4920"
	 
	body = "lol"
	msg.attach(MIMEText(body, 'plain'))
	 
	server = smtplib.SMTP('smtp-mail.outlook.com', 587)
	server.starttls()
	server.login(fromaddr, <INSERT password>)
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.quit()

while True:
	for line in page.iter_lines():
		if "Tue 12:00 - 14:00 (Weeks:2-9,10-13), Thu 17:00 - 18:00 (Weeks:2-9,10-13)" in line.decode("utf-8") or "Tue 16:00 - 18:00 (Weeks:2-9,10-13), Thu 14:00 - 15:00 (Weeks:2-9,10-13)" in line.decode("utf-8"):
			if "24/24" not in prev:
				email()
		prev = line.decode("utf-8")
	print("sleep for 5 minutes",flush=True)
	time.sleep(300)
	
