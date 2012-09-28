from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
import time
from selenium import selenium, common

from selenium.webdriver.support.ui import WebDriverWait

# Create a new instance of the Firefox driver
driver = webdriver.Firefox()

driver.get("http://localhost:8080/networking/Fall2012/preview/?login")

inputElementUsername = driver.find_element_by_id("id_username")
inputElementPassword = driver.find_element_by_id("id_password")

#login
inputElementUsername.send_keys("professor_0")
inputElementPassword.send_keys("class2go")
inputElementPassword.submit()

courseIntroVideo = driver.find_element_by_link_text("Course Introduction")
courseIntroVideo.click()
    
time.sleep(10)
driver.execute_script("player.playVideo();")

print driver.title