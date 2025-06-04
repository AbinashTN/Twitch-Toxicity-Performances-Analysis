from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import sys

# instantiate a Chrome options object with headlesss mode
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")

# initialize an instance of the chrome driver (browser) in headless mode
driver = webdriver.Chrome(
    options=options,
)

link = sys.argv[1]

# visit target site
driver.get(link)

# wait 5 seconds for the page to load
time.sleep(5)

#get the category
category = driver.find_element(By.CSS_SELECTOR, "p.CoreText-sc-1txzju1-0.hXbANI").text
print(category)

# release the resources allocated by Selenium and shut down the browser
driver.quit()


