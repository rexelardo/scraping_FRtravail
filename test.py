from selenium import webdriver

driver = webdriver.Chrome()
print(driver.capabilities['chrome']['chromedriverVersion'])
driver.quit()
