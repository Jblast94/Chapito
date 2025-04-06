import time
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup, Tag

from chapito.config import Config
from chapito.tools.tools import create_driver, transfer_prompt

URL: str = "https://chat.inceptionlabs.ai/"
TIMEOUT_SECONDS: int = 120
SUBMIT_CSS_SELECTOR: str = 'div[role="button"]'
SUBMIT_DISABLE_CSS_SELECTOR: str = 'div[role="button"][aria-disabled="true"]'
ANSWER_XPATH: str = "//div[contains(@class, 'ds-markdown') and contains(@class, 'ds-markdown--block')]"


def check_if_chat_loaded(driver) -> bool:
    driver.implicitly_wait(5)
    try:
        button = driver.find_element(By.CSS_SELECTOR, SUBMIT_CSS_SELECTOR)
    except Exception as e:
        logging.warning("Can't find submit button in chat interface. Maybe it's not loaded yet.")
        return False
    return button is not None


def initialize_driver(config: Config):
    logging.info("Initializing browser for DeepSeek...")
    driver = create_driver(config)
    driver.get(URL)

    while not check_if_chat_loaded(driver):
        logging.info("Waiting for chat interface to load...")
        time.sleep(5)
    logging.info("Browser initialized")
    return driver


def send_request_and_get_response(driver, message):
    logging.debug("Send request to chatbot interface")
    driver.implicitly_wait(10)
    textarea = driver.find_element(By.TAG_NAME, "textarea")
    transfer_prompt(message, textarea)
    wait = WebDriverWait(driver, TIMEOUT_SECONDS)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SUBMIT_CSS_SELECTOR)))
    time.sleep(1)
    submit_buttons = driver.find_elements(By.CSS_SELECTOR, SUBMIT_CSS_SELECTOR)
    submit_button = submit_buttons[-1]
    logging.debug("Push submit button")
    submit_button.click()

    # Wait a little time to avoid early fail.
    time.sleep(3)

    # Wait for submit button to be available. It means answer is finished.
    wait = WebDriverWait(driver, TIMEOUT_SECONDS)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SUBMIT_DISABLE_CSS_SELECTOR)))

    time.sleep(1)
    message_bubbles = driver.find_elements(By.XPATH, ANSWER_XPATH)
    if not message_bubbles:
        logging.warning("No message found.")
        return ""
    last_message_bubble = message_bubbles[-1]
    html = last_message_bubble.get_attribute("outerHTML")
    clean_message = clean_chat_answer(html)
    logging.debug(f"Clean message ends with: {clean_message[-100:]}")
    return clean_message


def clean_chat_answer(html: str) -> str:
    """
    Find all DIVs containing code and remove unecessary decorations."
    """
    logging.debug("Clean chat answer")
    soup = BeautifulSoup(html, "html.parser")
    no_prose_divs = soup.find_all("div", class_="md-code-block")
    for div in no_prose_divs:
        if isinstance(div, Tag):
            code_tags = div.find_all("pre")
            div.clear()
            for code in code_tags:
                div.append(code)
        else:
            code_tags = []

    code_tags = soup.find_all("pre")
    for code_tag in code_tags:
        code_tag.insert_before("\n```\n")
        code_tag.insert_after("\n```\n")
    return soup.get_text().strip()


def main():
    driver = initialize_driver(Config())
    try:
        while True:
            user_request = input("Ask something (or 'quit'): ")
            if user_request.lower() == "quit":
                break
            response = send_request_and_get_response(driver, user_request)
            print("Answer:", response)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
