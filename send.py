from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Launch browser
driver = webdriver.Chrome()
driver.get("https://entreprise.francetravail.fr/recherche-profil/rechercheprofil")
driver.set_window_size(1440, 830)

# Wait for profiles to load (you might need WebDriverWait here for stability)
time.sleep(5)

# Find all profile elements by their shared class or attribute
profiles = driver.find_elements(By.CSS_SELECTOR, ".media-body .lienclic-profil")

for profile in profiles:
    try:
        profile.click()
        time.sleep(2)  # Wait for profile detail page to load

        # Click contact button
        driver.find_element(By.ID, "boutonMiseEnContact").click()
        time.sleep(1)

        # Fill in subject
        driver.find_element(By.ID, "contact-objet").send_keys("Développeur Web")
        time.sleep(1)

        # Fill in message (you might need to update this ID if it's dynamic)
        message_box = driver.find_element(By.CSS_SELECTOR, "textarea[id^='contactMessage']")
        message_box.send_keys("Bonjour, je suis intéressé par votre profil. Seriez-vous disponible pour un échange ?")

        # Submit form (find the actual send button)
        # driver.find_element(By.ID, "sendButtonId").click()

        # Optional: go back to profile list
        driver.back()
        time.sleep(2)

    except Exception as e:
        print(f"Failed on a profile: {e}")
        driver.back()
        time.sleep(2)

driver.quit()
