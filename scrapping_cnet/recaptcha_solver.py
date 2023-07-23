import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import whisper
import requests
import time

def click_reload(driver):
    '''
    This function reloads the captcha when it is active
    '''
    
    try:
        print("Reloading captcha...")
        driver.find_element(By.ID, "recaptcha-reload-button").click()
        time.sleep(1)
    except:
        print("Could not reload the audio source")
    

def transcribe(url):
    '''
    This function transcribes the audio into text using whisper
    '''
    
    try:
        model = whisper.load_model("base")
        with open('audio.mp3', 'wb') as f:
            f.write(requests.get(url).content)
        result = model.transcribe('audio.mp3')
        return result["text"].strip()
    except:
        print("Error in transcribing function")
        raise

def click_checkbox(driver):
    '''
    This function transcribes clicks the checkbox to start the captcha process
    '''
    try:
        driver.switch_to.default_content()
        driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, 'iframe[title="reCAPTCHA"]'))
        driver.find_element(By.ID, "recaptcha-anchor-label").click()
        driver.switch_to.default_content()
    except:
        print("Error in clicking checkbox")
        pass


def request_audio_version(driver):
    '''
    This function requests the captcha audio version to solve it
    '''
    try:
        driver.switch_to.default_content()
        driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, 'iframe[title="El reCAPTCHA caduca dentro de dos minutos"]'))
        driver.find_element(By.ID, "recaptcha-audio-button").click()

    except:
        print("Error in requesting audio captcha")
        return None

def solve_audio_captcha(driver):
    '''
    This function solves the captcha and sends the solution to complete it
    '''
    try:
        text = transcribe(driver.find_element(By.ID, "audio-source").get_attribute('src'))
        driver.find_element(By.ID, "audio-response").send_keys(text)
        driver.find_element(By.ID, "recaptcha-verify-button").click()
    
    except:
        print("Error in solving audio captcha")
        raise

def recaptchav2_solver(driver):
    '''
    This function tries to solve the captcha 20 times and have some troubleshooting:
    Sometimes audio won't load, the transcriber would fail...
    '''
    for i in range(0,20):
        #if there is no captcha already "activated" then click and solve it
        if len(driver.find_elements(By.CSS_SELECTOR, 'iframe[title="reCAPTCHA"]')) > 0:
            try:
                print("Solving captcha in attempt",i)
                click_checkbox(driver)
                time.sleep(2)
                request_audio_version(driver)
                time.sleep(2)
                solve_audio_captcha(driver)
                time.sleep(5)
                #if we do not find the audio-response element - captcha is solved!
                if len(driver.find_elements(By.ID, "audio-response")) == 0:
                    print("Captcha/s completed correctly in",i)
                    break
                else:
                    continue
                
            except:
                print("Captcha failed in",i)
                print("Refreshing and trying again...")
                # we refresh the page if we fail
                driver.refresh()
                time.sleep(1)
                continue
        #if there is a audio-response element then we might have failed the captcha
        #then we reload the captcha and try again
        elif len(driver.find_elements(By.ID, "audio-response")) > 0:
            click_reload(driver)
            try:
                print("Solving captcha in attempt",i)
                print("Reloaded and trying again....")
                solve_audio_captcha(driver)
                time.sleep(2)
                #Again if it's solved we break the loop
                if len(driver.find_elements(By.ID, "audio-response")) == 0:
                    print("Captcha/s completed correctly in",i)
                    break
                else:
                    pass

                time.sleep(5)
            except:
                print("Failed retrying captcha")
                continue

        else:
            break



if __name__ == "__main__":

    #Execute this script to test it in demo captcha from google
    
    GOOGLE_USER = "YOUR_USER"

    GOOGLE_PASS = "YOUR_PASS"

    options = uc.ChromeOptions()

    headless = False

    driver = uc.Chrome(options = options, headless = headless)

    wait = WebDriverWait(driver,30)

    driver.get("https://accounts.google.com/")
    e = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "input[type='email']")))
    e.send_keys(GOOGLE_USER)
    e.send_keys(Keys.ENTER)
    e = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password']")))
    e.send_keys(GOOGLE_PASS)
    e.send_keys(Keys.ENTER)
    driver.get("https://www.google.com/recaptcha/api2/demo")
    recaptchav2_solver(driver = driver)
    time.sleep(10)
    driver.quit()


