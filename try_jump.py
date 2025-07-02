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
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--remote-debugging-port=9222")  # enable DevTools
    driver = webdriver.Chrome(options=options)
    driver.get(
        "https://entreprise.francetravail.fr/connexion/XUI/?realm=/employeur&goto=https://entreprise.francetravail.fr/connexion/oauth2/realms/root/realms/employeur/authorize?realm%3D/employeur%26response_type%3Did_token%2520token%2520code%26scope%3Dopenid%2520profile%2520email%2520application_ENT_PO018-PORTAILENTREPRISE%2520rechercheProfil%26client_id%3DENT_PO018-PORTAILENTREPRISE_C2356069E9D1E79CA924378153CFBBFB66C5319DB%26state%3Dx0UX3g6FuHO7nQXO%26nonce%3DcDv4Vr6nR6woM6qg%26redirect_uri%3Dhttps://entreprise.pole-emploi.fr/accueil/connecte/#login/"
    )
    input("Login manually and press Enter to continue...\n")
    return driver


def safe_click(driver, element, retries=3, pause=1.0):
    """
    Safely click an element with retries for intercepts and stale references.
    """
    for attempt in range(retries):
        try:
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", element
            )
            time.sleep(0.5)
            element.click()
            return
        except (ElementClickInterceptedException, StaleElementReferenceException) as e:
            if attempt < retries - 1:
                time.sleep(pause)
                continue
            else:
                try:
                    driver.execute_script("arguments[0].click();", element)
                    return
                except Exception as js_e:
                    raise Exception(f"Click failed even with JS fallback: {js_e}")



def open_profile_n(driver, target_n, batch_size=10):
    counter = 0
    more_btn_xpath = "//button[contains(@onclick, 'rafraichirUneZoneCvAvecRecherche')]"
    profile_buttons_xpath = "//button[contains(@onclick, 'xiti_titreProfil')]"

    while counter < target_n:
        try:
            more_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, more_btn_xpath))
            )
            safe_click(driver, more_btn)
            counter += batch_size
            time.sleep(1.2)  # give DOM time to update
        except Exception as e:
            print(f"Error loading next batch: {e}")
            time.sleep(2)
            continue

    # Click the last profile button after final batch
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, profile_buttons_xpath))
        )
        profile_buttons = driver.find_elements(By.XPATH, profile_buttons_xpath)
        final_button = profile_buttons[-2]  # second to last button
        safe_click(driver, final_button)
    except Exception as e:
        print(f"Error clicking final profile: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    driver = setup_driver()
    open_profile_n(driver, 420)
    # keep browser open for inspection
    time.sleep(120)
