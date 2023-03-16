import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
from rich import print
import time

class EmailService:
    def __init__(self, to, subject, body):
        self.from_email     = 'INSERT_EMAIL_ADDRESS_HERE'
        self.from_password  = 'INSERT_EMAIL_PASSWORD_HERE'
        self.smtp_server    = 'smtp.gmail.com' # 'smtp.gmail.com' for Gmail
        self.bcc            = 'INSERT_EMAIL_ADDRESS_HERE'
        self.smtp_port      = 465 # 465 for Gmail
        self.to      = to
        self.subject = subject
        self.body    = body
        self.today   = datetime.datetime.now()
    
    def send(self):
        server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
        server.ehlo()
        server.login(self.from_email, self.from_password)

        message = MIMEMultipart()
        message['Subject'] = self.subject
        messageBody = self.body
        message['From'] = self.from_email
        message['To'] = self.to
        message.add_header('Bcc', self.bcc)
        part = MIMEText(messageBody, 'plain')
        message.attach(part)

        server.sendmail(self.from_email, self.to, message.as_string())
        server.close()
        print('Email sent successfully!')

class Inventory:
    def __init__(self):
        self.API_URL = "https://www.tesla.com/inventory/api/v1/inventory-results"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://www.tesla.com/en_IE/inventory/new/my?arrangeby=relevance&zip=&range=0",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }
        self.querystring = {"query":"{\"query\":{\"model\":\"my\",\"condition\":\"new\",\"options\":{},\"arrangeby\":\"Relevance\",\"order\":\"desc\",\"market\":\"IE\",\"language\":\"en\",\"super_region\":\"north america\",\"lng\":\"\",\"lat\":\"\",\"zip\":\"\",\"range\":0},\"offset\":0,\"count\":50,\"outsideOffset\":0,\"outsideSearch\":false}"}
        self.VIN_HISTORY = []
        self.SPAM_DETECTION = True

    def check_inventory(self):
        response = requests.request("GET", self.API_URL, headers=self.headers, params=self.querystring)
        NUM_VEHICLES = 0
        OK_VEHICLES = 0
        for vehicle in response.json()['results']:
            NUM_VEHICLES += 1
            if self.SPAM_DETECTION or vehicle['InventoryPrice'] > 70000 or vehicle['VIN'] in self.VIN_HISTORY:
                continue
            OK_VEHICLES += 1
            self.VIN_HISTORY.append(vehicle['VIN'])
            email_body = open('email_body.txt', 'r').read()
            email_body = email_body.replace('[INSERT_TRIM_HERE]', vehicle['TrimName'])
            email_body = email_body.replace('[INSERT_CITY_HERE]', vehicle['City'])
            email_body = email_body.replace('[INSERT_PRICE_HERE]', str(vehicle['InventoryPrice']))
            email_body = email_body.replace('[INSERT_URL_HERE]', 'https://www.tesla.com/en_IE/my/order/' + vehicle['VIN'])
            EmailService('INSERT_EMAIL_ADDRESS_HERE', f'New Tesla Model Y listed ({str(vehicle["InventoryPrice"])} EUR)', email_body).send()
            time.sleep(1)
        print(f'Checked inventory. Found {NUM_VEHICLES} vehicles. {OK_VEHICLES} vehicles are OK. (Spam detection: {self.SPAM_DETECTION})')

        if self.SPAM_DETECTION:
            self.SPAM_DETECTION = False

if __name__ == '__main__':
    inventory = Inventory()
    while True:
        try:
            inventory.check_inventory()
        except Exception as err:
            print(err)
        time.sleep(30)