import os
import time
import random
import json
import logging
import pdb
import argparse
from datetime import datetime, timedelta
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

# Constants
DATABASE_FILE = "contacted_users.csv"
CHECKPOINT_FILE = "last_profile_checkpoint.json"
LOG_FILE = "scraper.log"
ERROR_DIR = "errors"

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

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# Utility functions

def load_contacted_users():
    if os.path.exists(DATABASE_FILE):
        return pd.read_csv(DATABASE_FILE)
    return pd.DataFrame(columns=["user_name"])


def save_contacted_users(df):
    df.to_csv(DATABASE_FILE, index=False)


def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return json.load(f).get("last_index", 1)
    return 1


def save_checkpoint(index):
    os.makedirs(ERROR_DIR, exist_ok=True)
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"last_index": index}, f)


def random_delay(min_sec=1, max_sec=3):
    time.sleep(random.uniform(min_sec, max_sec))


def take_error_snapshot(driver, name, stage):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.join(ERROR_DIR, f"{name}_{stage}_{timestamp}")
    driver.save_screenshot(f"{base}.png")
    with open(f"{base}.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    logging.info("Saved error snapshot for %s at %s", name, base)


def close_modal_if_present(driver):
        """Enhanced modal closing with multiple attempts"""
        modal_selectors = [
            (By.ID, "PopinMiseEnContact"),
            (By.CSS_SELECTOR, ".modal"),
            (By.CSS_SELECTOR, "[role='dialog']"),
            (By.CSS_SELECTOR, ".popup")
        ]
        
        for selector in modal_selectors:
            try:
                modal = WebDriverWait(driver, 5).until(EC.visibility_of_element_located(selector))
                # Try multiple close button patterns
                close_selectors = [
                    "//button[normalize-space(text())='Fermer']",
                    "//button[contains(@class, 'close')]",
                    "//button[@aria-label='Close']",
                    "//*[contains(@class, 'close')]"
                ]
                
                for close_selector in close_selectors:
                    try:
                        fermer = WebDriverWait(driver, 2).until(
                            EC.element_to_be_clickable((By.XPATH, close_selector))
                        )
                        fermer.click()
                        WebDriverWait(driver, 5).until(EC.invisibility_of_element_located(selector))
                        logging.info("Successfully closed modal")
                        random_delay()
                        return True
                    except:
                        continue
            except:
                continue
        return False

# Core functions

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--remote-debugging-port=9222")  # enable DevTools
    driver = webdriver.Chrome(options=options)
    driver.get(
        "https://entreprise.francetravail.fr/connexion/XUI/?realm=/employeur&goto=https://entreprise.francetravail.fr/connexion/oauth2/realms/root/realms/employeur/authorize?realm%3D/employeur%26response_type%3Did_token%2520token%2520code%26scope%3Dopenid%2520profile%2520email%2520application_ENT_PO018-PORTAILENTREPRISE%2520rechercheProfil%26client_id%3DENT_PO018-PORTAILENTREPRISE_C2356069E9D1E79CA924378153CFBBFB4D4416B1F99D41A2940BFDB66C5319DB%26state%3Dx0UX3g6FuHO7nQXO%26nonce%3DcDv4Vr6nR6woM6qg%26redirect_uri%3Dhttps://entreprise.pole-emploi.fr/accueil/connecte/#login/"
    )
    input("Login manually and press Enter to continue...\n")
    return driver


def send_message(driver, message, name, stage):
    try:
        contact_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "boutonMiseEnContact"))
        )
        contact_button.click(); random_delay()

        subject_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "contact-objet"))
        )
        subject_input.click(); subject_input.send_keys("Proposition Growth Hacker"); random_delay()

        textareas = driver.find_elements(By.CSS_SELECTOR, "div.form-group textarea")
        for textarea in textareas:
            if "contactMessage" in textarea.get_attribute("id"):
                textarea.clear(); textarea.send_keys(message); random_delay()

        checkbox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='contact-moyens-input-1']"))
        )
        checkbox.click(); random_delay()

        envoyer = driver.find_element(By.CSS_SELECTOR, "#submitButtonEnvoyerProposition")
        envoyer.click(); random_delay()

        popup_close = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='PopinMiseEnContact']//button"))
        )
        popup_close.click(); random_delay()

        logging.info("%s message sent for %s", stage, name)
    except Exception:
        logging.exception("Error sending %s message for %s", stage, name)
        take_error_snapshot(driver, name, stage)
        close_modal_if_present(driver)


def has_been_contacted(driver):
    try:
        badge = driver.find_element(
            By.CSS_SELECTOR,
            "#zoneAfficherDetailProfil li.badge-last-contact"
        )
        return "Déjà contacté" in badge.text
    except:
        return False


def email_flow(driver, contacted_df):
    name_elem = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "h2.name.t3 span"))
    )
    name = name_elem.text.strip()
    if name in contacted_df["user_name"].values or has_been_contacted(driver):
        logging.info("Skipping already contacted: %s", name)
        return contacted_df

    logging.info("Processing user: %s", name)
    # pdb.set_trace()  # uncomment to enter debugger here

    send_message(driver, INITIAL_MESSAGE, name, "initial")
    send_message(driver, FOLLOWUP_MESSAGE, name, "followup")

    new = pd.DataFrame({"user_name": [name]})
    updated = pd.concat([contacted_df, new], ignore_index=True)
    save_contacted_users(updated)
    logging.info("Recorded %s to database", name)
    return updated


def navigate_profiles(driver):
    current_index = load_checkpoint()
    contacted_df = load_contacted_users()
    counter = current_index
    session_start = datetime.now()
    logging.info("Session started at %s", session_start)

    while True:
        try:
            contacted_df = email_flow(driver, contacted_df)
            save_checkpoint(counter)

            # attempt navigation
            next_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@title='Suivant']"))
            )
            try:
                next_btn.click(); random_delay()
            except ElementClickInterceptedException:
                logging.warning("Click intercepted at profile %s, closing modal and retrying", counter)
                take_error_snapshot(driver, f"intercept_{counter}", "navigation")
                close_modal_if_present(driver)
                next_btn.click(); random_delay()

            if counter % 5 == 0:
                time.sleep(random.uniform(3, 8))

            counter += 1
        except TimeoutException:
            logging.info("No more profiles or timeout at index %s", counter)
            break
        except Exception as e:
            logging.exception("Unexpected error at index %s", counter)
            take_error_snapshot(driver, f"loop_{counter}", "navigation")
            # allow interactive debugging without closing browser
            print(f"Error at profile {counter}: {e}")
            print("Entering interactive debugger. Fix in browser, then 'c' to continue or 'q' to quit.")
            pdb.set_trace()
            # after debugging, retry or skip
            choice = input("[r]etry, [s]kip, [q]uit: ").strip().lower()
            if choice == 'q':
                break
            elif choice == 's':
                counter += 1
                continue
            # else retry current profile

    session_end = datetime.now()
    duration = session_end - session_start
    logging.info(
        "Session ended at %s after %s profiles, duration %s",
        session_end, counter, duration
    )

if __name__ == "__main__":
    os.makedirs(ERROR_DIR, exist_ok=True)
    driver = setup_driver()
    try:
        first = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@onclick, 'xiti_titreProfil(0)')]"))
        )
        first.click(); time.sleep(3)
    except TimeoutException:
        logging.warning("First profile button not found")

    navigate_profiles(driver)
