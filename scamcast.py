from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sendgrid
import json

with open("config.json") as config_file:
  config_data = json.loads(config_file.read())

COMCAST_USER = config_data["comcast"]["user"]
COMCAST_PASS = config_data["comcast"]["pass"]

SENDGRID_USER = config_data["sendgrid"]["user"]
SENDGRID_PASS = config_data["sendgrid"]["pass"]
SENDGRID_FROM = "%s <%s>" % (config_data["sendgrid"]["from"]["name"], config_data["sendgrid"]["from"]["email"])

RECIPIENTS = config_data["recipients"]

def RetrieveUsage():
  driver = webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')
  driver.set_window_size(1120, 550)
  print "Logging into xfinity.com"
  driver.get("https://customer.xfinity.com/MyServices/Internet")
  driver.find_element_by_id("user").send_keys(COMCAST_USER)
  driver.find_element_by_id("passwd").send_keys(COMCAST_PASS)
  driver.find_element_by_id("sign_in").click()
  while driver.current_url != "https://customer.xfinity.com/MyServices/Internet/":
      print "Loading..."
      time.sleep(5)
  print "Logged in at: "
  print driver.current_url
  element = WebDriverWait(driver, 30).until(
      EC.presence_of_element_located((By.CLASS_NAME, "cui-usage-label"))
  )
  #find span under div with class cui-usage-label
  usage = driver.find_element_by_class_name("cui-usage-label").find_element_by_tag_name("span").text
  driver.quit()
  print usage
  return usage

def SendEmails(content):
  print "Sending email alert"
  sg = sendgrid.SendGridClient(SENDGRID_USER, SENDGRID_PASS)
  message = sendgrid.Mail()
  for recipient in RECIPIENTS:
    message.add_to('%s <%s>' % (recipient["name"],recipient["email"]))
  message.set_subject(content)
  message.set_text(content)
  message.set_from(SENDGRID_FROM)
  status, msg = sg.send(message)
  print "Message result:" + msg

usage = RetrieveUsage()
SendEmails('Comcast Usage:' + usage)


