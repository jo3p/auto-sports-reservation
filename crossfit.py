import datetime
import pause
import time
import sys
import os
from getpass import getpass

from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from seleniumrequests import Chrome
from helpers import WebDriver, chrome_options

# get credentials
which_user = input("Make a reservation for? (joep/vera)")
if which_user == "joep":
    username = os.environ['EMAIL_JOEP']
    password = os.environ['PW_JOEP']
elif which_user == "vera":
    username = os.environ['EMAIL_VERA']
    password = os.environ['PW_VERA']
else:
    print("User not recognized. Please fill in credentials manually below.")
    username = input("What is your login e-mailaddress?\n")
    password = getpass("What is your password?\n")  # getpass is used in order to securely input the password

reservation_date_string = input("Give in a date in the following format: dd-mm-yyyy\n")
reservation_start_time_string = input("Give in a start time in the following format: hh:mm\n")
reservation_date_datetime = datetime.datetime.strptime(reservation_date_string, "%d-%m-%Y")

# check if reservation date is within 7 days, if not: wait
if (reservation_date_datetime - datetime.timedelta(days=7)) > datetime.datetime.now():
    postponed = True
    execution_date_datetime = reservation_date_datetime - datetime.timedelta(days=7)
    login_datetime = execution_date_datetime - datetime.timedelta(seconds=120)
    pause.until(login_datetime)
else:
    execution_date_datetime = reservation_date_datetime
    postponed = False

# instantiate WebDriver
with WebDriver(Chrome(options=chrome_options)) as driver:
    # retrieve login page
    driver.get("https://crossfitclubpiushaven.sportbitapp.nl/cbm/account/inloggen/")
    time.sleep(3)

    # fill credentials
    username_elem = driver.find_element_by_name("username")
    username_elem.click()
    username_elem.clear()
    username_elem.send_keys(username)
    time.sleep(1)
    password_elem = driver.find_element_by_name("password")
    password_elem.click()
    password_elem.clear()
    password_elem.send_keys(password)
    password_elem.send_keys(Keys.RETURN)
    time.sleep(2)

    # go to the right overview page by weeknumber
    weeknumber = reservation_date_datetime.isocalendar()[1]  # convert reservation date to week number
    year = reservation_date_datetime.isocalendar()[0]  # convert reservation date to year
    driver.get(
        f"https://crossfitclubpiushaven.sportbitapp.nl/cbm/account/lesmomenten/?year={year}&week={weeknumber}")
    time.sleep(1)

    try:
        lesson_url = driver.find_element_by_css_selector(
            f'[href*="training-info/{reservation_date_string}/{reservation_start_time_string}"]').get_attribute("href")
    except NoSuchElementException as e:
        lesson_url = 'https://crossfitclubpiushaven.sportbitapp.nl/cbm/' + driver.find_element_by_css_selector(
            f'[data-href*="training-info/{reservation_date_string}/{reservation_start_time_string}"]') \
            .get_attribute("data-href")
    enrol_url = lesson_url + "aanmelden"
    time.sleep(1)

    # if the login was postponed before, execute the actual booking 1sec past midnight
    if postponed:
        send_request_datetime = execution_date_datetime + datetime.timedelta(seconds=1)
        pause.until(send_request_datetime)

    driver.get(enrol_url)
