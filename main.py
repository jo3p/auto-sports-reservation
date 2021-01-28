# imports
import datetime
import pause
import time
import platform
from getpass import getpass

from selenium.webdriver.common.keys import Keys
from seleniumrequests import Chrome
from selenium.webdriver.chrome.options import Options
from helpers import WebDriver

if platform.system() == 'Linux':
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
else:
    chrome_options = Options()

# get user input
sport = input('What do you want to (de)-enrol for? Format: [tennis/crossfit]\n')

if sport == 'tennis':
    # get user input
    username = input('What is your student number?\n')
    password = getpass('What is your password?\n')  # getpass is used in order to securely input the password
    reservation_date_string = input('Give in a date in the following format: dd-mm-yyyy\n')
    reservation_start_time_string = input('Give in a start time in the following format: hh:mm\n')
    reservation_date_datetime = datetime.datetime.strptime(reservation_date_string, '%d-%m-%Y')

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
        driver.get('https://dmsonline.uvt.nl/en/auth/connect_uvt')
        time.sleep(3)

        # search for the right University to be redirected to the logon page
        search_bar = driver.find_element_by_css_selector('.mod-search-input')
        search_bar.click()
        search_bar.send_keys('Tilburg')
        search_bar.send_keys(Keys.RETURN)
        time.sleep(3)

        # fill credentials
        username_elem = driver.find_element_by_id('username')
        username_elem.click()
        username_elem.clear()
        username_elem.send_keys(username)
        time.sleep(1)
        password_elem = driver.find_element_by_id('password')
        password_elem.click()
        password_elem.clear()
        password_elem.send_keys(password)
        password_elem.send_keys(Keys.RETURN)
        time.sleep(2)

        # navigating to the new reservation page
        driver.get('https://dmsonline.uvt.nl/en/bookings/view/new')
        time.sleep(1)

        # retrieve the cross site reference forgery (csrf) token from the new bookings html page
        csrf_token = driver.find_element_by_name('csrf_token').get_attribute('value')

        # reverse the date in desired format
        reservation_date_reversed_string = datetime.datetime.strftime(reservation_date_datetime, '%Y-%m-%d')

        # concatenate date and time into required format
        desired_start = reservation_date_reversed_string + ' ' + reservation_start_time_string

        # add 59 minutes to desired_start to create desired_end
        desired_start_datetime = datetime.datetime.strptime(desired_start, '%Y-%m-%d %H:%M')
        desired_end_datetime = desired_start_datetime + datetime.timedelta(minutes=59)
        desired_end = desired_end_datetime.strftime('%Y-%m-%d %H:%M')
        # creating the booking POST-method payload
        booking_payload = {
            'product_id': '385',
            'site_id': "0",
            'csrf_token': csrf_token,
            'startDate': desired_start,
            'endDate': desired_end,
            'maxParticipants': '4',

        }

        # if the login was postponed before, execute the actual booking 1sec past midnight
        if postponed:
            send_request_datetime = execution_date_datetime + datetime.timedelta(seconds=3)
            pause.until(send_request_datetime)

        # make actual booking
        add_booking_url = 'https://dmsonline.uvt.nl/en/bookings/addBooking'
        driver.request('POST', add_booking_url, data=booking_payload)

elif sport == 'crossfit':
    # get user input
    username = input("What is your login e-mailaddress?\n")
    password = getpass("What is your password?\n")  # getpass is used in order to securely input the password
    reservation_date_string = input("Give in a date in the following format: dd-mm-yyyy\n")
    reservation_start_time_string = input("Give in a start time in the following format: hh:mm\n")
    reservation_date_datetime = datetime.datetime.strptime(reservation_date_string, '%d-%m-%Y')

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

        # retrieve the sign-on url from the overview webpage
        lesson_url = driver.find_element_by_css_selector(
            f'[data-date="{reservation_date_string}"][data-time-start="{reservation_start_time_string}"]') \
            .get_attribute('href')
        enrol_url = lesson_url + "aanmelden"
        time.sleep(1)

        # if the login was postponed before, execute the actual booking 1sec past midnight
        if postponed:
            send_request_datetime = execution_date_datetime + datetime.timedelta(seconds=3)
            pause.until(send_request_datetime)

        driver.get(enrol_url)
