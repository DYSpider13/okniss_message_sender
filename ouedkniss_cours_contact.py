# coding: utf-8

import requests as req
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import re
import datetime
import sys
import json

# Check if a date is in the last week
def checkDateCondition(dateTimeStr):

    date = re.findall("(\d+)\/(\d+)\/(\d+)", dateTimeStr)
    if len(date) == 0:
        return True
    
    date = '-'.join(date[0])
    date = datetime.datetime.strptime(date, "%d-%m-%Y")
    today = datetime.datetime.now()

    print((today - date).days)

    return (((today - date).days) < 60)


# ---> Reading arguments in file
if len(sys.argv) == 1: 
    print("Usage: " + sys.argv[0] + " [param_file.json]")
    sys.exit(0)

paramFile = sys.argv[1]
params = {}

with open(paramFile, "r") as f:
    try:
        params = json.load(f)
    except:
        print("Error reading params from file. Exiting")
        sys.exit(0)


url = "https://www.ouedkniss.com/cours-r"
urlMain = "https://www.ouedkniss.com"

# ---> Opening the driver & query the URL
driver = webdriver.ChromeOptions()
driver = webdriver.Chrome("/home/spider/Bureau/divers/chromedriver")
driver.get(urlMain)




# ---> Login
driver.find_element_by_id("menu_seconnecter").click()

wait = WebDriverWait(driver, 20)
element = wait.until(EC.presence_of_element_located((By.NAME, 'username')))

driver.switch_to_active_element()

driver.find_element_by_name("username").send_keys(params["username"])
driver.find_element_by_name("password").send_keys(params["pwd"])
driver.find_element_by_id("login_submit").click()


driver.get(url)
cnt = 0

while True:

    for announce in driver.find_elements_by_class_name("annonce"):
        #announce.find_element_by_xpath('.//div[@class="annonce_buttons"]/*a[@class=button_message]').click()

        try:
            cat = announce.find_element_by_class_name("annonce_get_description").text
        except:
            continue

        if params["category"].lower() not in cat.lower():
            print("Category is " + cat + " --> Passing")
            continue

        try:
            announce.find_element_by_class_name('button_message').click()
        except:
            continue

        # Check if we did not contacted the person for at least one week
        try:
            element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'chatbox_open')))
        except:
            print("Chatbox did not open")
            continue

        iframe = driver.find_elements_by_tag_name('iframe')[0]
        driver.switch_to_frame(iframe)

        driver.find_element_by_class_name("Messenger")

        msg_box = driver.find_element_by_id("divData")
        # loop over messages
        try:
            wait = WebDriverWait(driver, 3)
            element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'im')))
        except:
            print("No messages ? ")

        last_time = ""
        msgs = msg_box.find_elements_by_class_name("im")
        print("Nb of messages: "  + str(len(msgs)))
        for msg in msgs:
            try:
                last_time = msg.find_element_by_class_name("message_time").text 
                print("Msg time is: " + last_time)             
            except:
                print("Could not find message time")
                continue


        if checkDateCondition(last_time) == False or len(msgs) == 0:
            textField = driver.find_element_by_xpath("//textarea")
            textField.send_keys(params["messageFrench"])
            #textField.send_keys(Keys.ENTER)
            driver.execute_script("document.getElementById('envoyer').click()")
            cnt = cnt + 1
        else:
            print("Passing this announce")

        time.sleep(5)
        # close chat
        driver.switch_to_default_content()
        driver.execute_script("document.getElementsByClassName('CloseChat')[0].click()")


    if cnt == params["limit"]:
        break
    
    # go to second page
    driver.find_element_by_class_name("page_arrow").click()

print("Finished ! ")
print("Sent: " + cnt + " messages")
