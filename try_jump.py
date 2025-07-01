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
    Safely click an element, retrying on intercepts and scrolling into view.
    Falls back to JS click on final attempt.
    """
    for attempt in range(retries):
        try:
            # scroll into center view
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                element
            )
            time.sleep(0.1)
            element.click()
            return
        except ElementClickInterceptedException:
            if attempt < retries - 1:
                time.sleep(pause)
                continue
            # final fallback: JS click
            driver.execute_script("arguments[0].click();", element)
            return


def open_profile_n(driver, target_n, batch_size=10):
    """
    Load batches of profiles until the Nth profile detail button is visible,
    then click it safely.
    target_n is 1-based; xiti_titreProfil wants zero-based.
    """
    counter = 0
    zero_idx = target_n - 1
    more_btn_xpath = "//button[contains(@onclick, 'rafraichirUneZoneCvAvecRecherche')]"
    detail_btn_xpath = f"//button[contains(@onclick, 'xiti_titreProfil({zero_idx})')]"
    final_detail_btn_xpath = f"//button[contains(@onclick, 'xiti_titreProfil({target_n%10})')]"

    while counter < target_n:
        try:
            # look for the detail button
            detail_btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, final_detail_btn_xpath))
            )
            safe_click(driver, detail_btn)
            time.sleep(1)
            break
        except TimeoutException:
            # load next batch
            more_btn = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, more_btn_xpath))
            )
            safe_click(driver, more_btn)
            time.sleep(1)
            counter += batch_size


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    driver = setup_driver()
    open_profile_n(driver, 1000)
    # keep browser open for inspection
    time.sleep(120)
