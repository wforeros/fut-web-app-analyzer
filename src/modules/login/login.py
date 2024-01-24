import random
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def login(driver, user):
    try:
        WebDriverWait(driver, 15).until(
          EC.visibility_of_element_located(
            (By.XPATH, '//*[@class="ut-login-content"]//button'))
        )

        sleep(random.randint(2, 4))
        driver.find_element(
          By.XPATH, '//*[@class="ut-login-content"]//button').click()

        WebDriverWait(driver, 10).until(
          EC.visibility_of_element_located((By.ID, 'email'))
        )

        sleep(1)
        driver.find_element(By.ID, 'email').send_keys(user["email"])
        sleep(1)
        driver.find_element(By.ID, 'password').send_keys(user["password"])
        sleep(1)
        driver.find_element(
            By.XPATH, '/html/body/div[1]/div[2]/section/div[1]/form/div[6]/a').click()
        sleep(3)

        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable(
                (By.XPATH, '/html/body/div/form/div/section/a[2]'))
        ).click()

        print("Continue login manually")
    except:
        print("Continue login manually")
