# imports
import datetime
import pause
import time
from getpass import getpass

from selenium.webdriver.common.keys import Keys
from seleniumrequests import Chrome

# get user input
reservation_date = input('Give in a date in the following format: yyyy-mm-dd\n')
reservation_date_datetime = datetime.datetime.strptime(reservation_date, '%Y-%m-%d')
reservation_start_time = input('Give in a start time in the following format: hh:mm\n')
username = input('What is your student number to login?\n')
password = getpass('What is your password?\n')  # getpass is used in order to securely input the password

# concatenate date and time into required format
desired_start = reservation_date + ' ' + reservation_start_time

# add 59 minutes to desired_start to create desired_end
desired_start_datetime = datetime.datetime.strptime(desired_start, '%Y-%m-%d %H:%M')
desired_end_datetime = desired_start_datetime + datetime.timedelta(minutes=59)
desired_end = desired_end_datetime.strftime('%Y-%m-%d %H:%M')

# check if reservation date is within 7 days, if not: wait
if (reservation_date_datetime - datetime.timedelta(days=7)) > datetime.datetime.now():
    postponed = True
    execution_date_datetime = reservation_date_datetime - datetime.timedelta(days=7)
    login_datetime = execution_date_datetime - datetime.timedelta(seconds=30)
    pause.until(login_datetime)

# opening a chrome session and navigating to the login page
driver = Chrome()
driver.get('https://dmsonline.uvt.nl/en/auth/connect_uvt')
time.sleep(3)

# search for the right University to be redirected to the logon page
search_bar = driver.find_element_by_css_selector('.mod-search-input')
search_bar.click()
search_bar.send_keys('Tilburg')
search_bar.send_keys(Keys.RETURN)
time.sleep(3)

# fill in the username and password
username_field = driver.find_element_by_id('username')
username_field.click()
username_field.clear()
username_field.send_keys(username)
time.sleep(1)
password_field = driver.find_element_by_id('password')
password_field.click()
password_field.send_keys(password)
password_field.send_keys(Keys.RETURN)
time.sleep(1)

# navigating to the new reservation page
driver.get('https://dmsonline.uvt.nl/en/bookings/view/new')
time.sleep(1)

# retrieve the cross site reference forgery (csrf) token from the new bookings html page
csrf_token = driver.find_element_by_name('csrf_token').get_attribute('value')

# creating the booking POST-method payload
booking_payload = {
    'product_id': '385',
    'site_id': "0",
    'csrf_token': csrf_token,
    'startDate': desired_start,
    'endDate': desired_end,
    'maxParticipants': '4',

}

# if the login was postponed before, execute the actual booking 3secs past midnight
if postponed:
    send_request_datetime = execution_date_datetime + datetime.timedelta(seconds=3)
    pause.until(send_request_datetime)

# make actual booking
add_booking_url = 'https://dmsonline.uvt.nl/en/bookings/addBooking'
driver.request('POST', add_booking_url, data=booking_payload)
