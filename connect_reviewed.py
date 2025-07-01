from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import pandas as pd
import os
from datetime import datetime, timedelta

# Path to contact history CSV
DATABASE_FILE = "contacted_users.csv"

# Message templates
INITIAL_MESSAGE = """
Salut, je me permets de te contacter en recherche d’un partenaire 
spécialisé en growth hacking et automatisation, passionné et ambitieux,
pour une startup innovante, ambitieuse et fun. Ce n’est pas un job de freelance
ou CDI, mais une opportunité de partenariat pour quelqu’un prêt à s’investir à 200%. 
Si tu te reconnais merci de :
"""

FOLLOWUP_MESSAGE = """
Peux-tu répondre avec un chiffre de 1 à 10 si tu maitrises :

1. Savoir coder Back-end ?
2. Le growth marketing et growth hacking ?
3. Savoir créer et optimiser des tunnels de vente ciblés et automatisés ?
4. Stratégies de lead generation en masse ?
5. ADS ultra ciblés et qualifiés ?
6. SEO et SEA ?
7. Extraction de données (numéros de téléphone, WhatsApp, emails) ?
8. Création de pages de capture ?
9. Mass mailing & SMS marketing ?
10. Automatisation de process via API, Selenium, Make ou autres outils ?
11. Développement/intégration de chatbots réseaux sociaux et appli. rencontre ?
12. Achat de comptes (linkedin, instagram, tiktok etc.) ?
13. Création d’app ? 
14. Automatisation avancée ?
15. OSINT, ingénierie sociale, hacking éthique ?
"""

def random_delay(min_sec=1, max_sec=3):
    time.sleep(random.uniform(min_sec, max_sec))

def setup_driver():
    driver = webdriver.Chrome()
    driver.get("https://entreprise.francetravail.fr/connexion/XUI/?realm=/employeur&goto=https://entreprise.francetravail.fr/connexion/oauth2/realms/root/realms/employeur/authorize?realm%3D/employeur%26response_type%3Did_token%2520token%2520code%26scope%3Dopenid%2520profile%2520email%2520application_ENT_PO018-PORTAILENTREPRISE%2520rechercheProfil%26client_id%3DENT_PO018-PORTAILENTREPRISE_C2356069E9D1E79CA924378153CFBBFB4D4416B1F99D41A2940BFDB66C5319DB%26state%3Dx0UX3g6FuHO7nQXO%26nonce%3DcDv4Vr6nR6woM6qg%26redirect_uri%3Dhttps://entreprise.pole-emploi.fr/accueil/connecte/#login/")
    print("Login manually and press Enter to continue...")
    input()
    return driver

def load_contacted_users():
    if os.path.exists(DATABASE_FILE):
        return pd.read_csv(DATABASE_FILE)
    return pd.DataFrame(columns=["user_name"])

def save_contacted_users(df):
    df.to_csv(DATABASE_FILE, index=False)

def send_message(driver, message):
    try:
        # Click on "Mise en contact" button
        contact_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "boutonMiseEnContact"))
        )
        contact_button.click()
        random_delay()

        # Set contact subject
        subject_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "contact-objet"))
        )
        subject_input.click()
        subject_input.send_keys("Proposition Growth Hacker")
        random_delay()

        # Fill the message
        textareas = driver.find_elements(By.CSS_SELECTOR, "div.form-group textarea")
        for textarea in textareas:
            if "contactMessage" in textarea.get_attribute("id"):
                textarea.clear()
                textarea.send_keys(message)
                random_delay()

        # Check the contact option
        checkbox_label = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='contact-moyens-input-1']"))
        )
        checkbox_label.click()
        random_delay()

        # Send the form
        envoyer_button = driver.find_element(By.CSS_SELECTOR, "#submitButtonEnvoyerProposition")
        envoyer_button.click()

        # Close confirmation popup
        popup_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='PopinMiseEnContact']//button"))
        )
        popup_button.click()
        random_delay()
    except TimeoutException as e:
        print("Timeout sending message:", e)

def email_flow(driver, contacted_users):
    try:
        name_element = driver.find_element(By.CSS_SELECTOR, "h2.name.t3 span")
        name = name_element.text.strip()
        print(f"Found user: {name}")
    except NoSuchElementException:
        print("User name not found.")
        return False

    if name in contacted_users["user_name"].values:
        print(f"Already contacted {name}, skipping...")
        return False

    send_message(driver, INITIAL_MESSAGE)
    send_message(driver, FOLLOWUP_MESSAGE)

    # Update the database
    new_entry = pd.DataFrame({'user_name': [name]})
    updated_df = pd.concat([contacted_users, new_entry], ignore_index=True)
    save_contacted_users(updated_df)

    print(f"✅ Total contacted in CSV: {len(updated_df)}")
    return True

def navigate_profiles(driver, start_counter=0):
    counter = start_counter
    session_contacts = 0
    contacted_users = load_contacted_users()

    while True:
        contacted = email_flow(driver, contacted_users)
        if contacted:
            session_contacts += 1
            print(f"📬 Contacted {session_contacts} users in this session.")

        try:
            next_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@title="Suivant"]/span[@aria-hidden="true"]'))
            )
            next_button.click()
            random_delay()
        except TimeoutException:
            print("Next button not found. Ending loop.")
            break

        counter += 1
        if counter % 5 == 0:
            print("⏸ Pausing longer after 5 profiles...")
            time.sleep(random.uniform(5, 15))

    print(f"🔚 Session complete. Total users contacted: {session_contacts}")

if __name__ == "__main__":
    driver = setup_driver()
    session_start = datetime.now()
    print(f"🚀 Session started at {session_start.strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        first_profile_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@onclick, 'xiti_titreProfil(0);')]"))
        )
        first_profile_button.click()
        time.sleep(3)
    except TimeoutException:
        print("Initial profile button not found.")

    navigate_profiles(driver)
    session_end = datetime.now()
    duration = session_end - session_start
    print(f"🏁 Session ended at {session_end.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🕒 Total session duration: {str(timedelta(seconds=int(duration.total_seconds())))}")
