import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import random
import csv

from recaptcha_solver import recaptchav2_solver

def click_next_page_button(driver, css = 'span.sui-AtomButton-rightIcon'):
    '''
    Finds last element with a rightIcon in the webpage (button where I can browse to next website page)
    To click it, we get parent of parent via XPATH ".."
    '''
    c = driver.find_elements(By.CSS_SELECTOR, css)[-1]

    p = c.find_element(By.XPATH, "..")

    pp = p.find_element(By.XPATH, "..")

    driver.execute_script("arguments[0].click();", pp)
    return None


def scroll_till_bottom(driver, wait_before_scroll = random.uniform(0.5,2)):
    '''
    Scrolls 500 pixels and wait "wait_before_scroll" before scrolling again
    '''
    for i in range(0,8500,500):
        scrolling = "window.scrollTo(0," 

        driver.execute_script(scrolling + str(i) + ")")

        time.sleep(wait_before_scroll)

    return None

def extract_brand_and_model(title, brands_list):
    #We extract the brand and model of a car
    #We have to do this because some brands have spaces in their name (e.g. ALFA ROMEO).
    #This way we ensure to extract correctly the full brand
    #Then we would get the next word as a model (e.g. ALFA ROMEO GIULIETTA)
    brand = ""
    model = ""
    check = False

    for j in brands_list:
        if j in title:
            brand = j
            model = title[len(j)+1::].split()[0]
            check = True
            break
        else:
            pass

    if check == False:
        brand = title.split()[0]
        model = title.split()[1]
    
    return brand, model

def extract_cars_info(car, brands_list):

    #We extract all the car info with CSS_SELECTORS
    try:
        link = car.find_element(By.CSS_SELECTOR, 'a[class="mt-CardBasic-titleLink"]').get_attribute('href')

        title = car.find_element(By.CSS_SELECTOR, 'a[class="mt-CardBasic-titleLink"]').get_attribute('title')

        price = car.find_element(By.CSS_SELECTOR, 'div[class="mt-CardAdPrice-cashAmount"]').text

        price = int(''.join(x for x in price if x.isdigit()))

        try:
            province = car.find_element(By.CSS_SELECTOR, 'div[class="mt-CardAd-attrItemIconLabel"]').text
            fuel, year, km = [i.text for i in car.find_elements(By.CSS_SELECTOR, 'li[class="mt-CardAd-attrItem"]')]

        except NoSuchElementException: 
            province, fuel, year, km = [i.text for i in car.find_elements(By.CSS_SELECTOR, 'li[class="mt-CardAd-attrItem"]')]   

        km = int(''.join(x for x in km if x.isdigit()))

        brand, model = extract_brand_and_model(title, brands_list)

    except:
        link = title = price = province = fuel = year = km = brand = model = "Error"

    return [link, title, price, province, fuel, year, km, brand, model]     


if __name__ == "__main__":

    #Start of the script
    #We log to Google because it can help reducing the amount of captchas that will appear during web scrapping
    
    GOOGLE_USER = "YOUR_USER"
    
    GOOGLE_PASS = "YOUR_PASS"
    
    options = uc.ChromeOptions()
    
    headless = True
    
    driver = uc.Chrome(options = options, headless = headless)
    
    wait = WebDriverWait(driver,30)
    
    print("Logging in Google Account...")
    
    driver.get("https://accounts.google.com/")
    
    e = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "input[type='email']")))
    e.send_keys(GOOGLE_USER)
    e.send_keys(Keys.ENTER)
    
    e = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password']")))
    e.send_keys(GOOGLE_PASS)
    e.send_keys(Keys.ENTER)
    
    print("Google Login completed")
    
    time.sleep(2)
    
    #After google login complete we go to the desired webpage
    
    driver.get('https://www.coches.net/segunda-mano/')
    
    time.sleep(random.uniform(0.5,1))
    
    #Find the button to accept the coookies. Tgen click it. Only once
    try:
        button = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="TcfAccept"]')
        driver.execute_script("arguments[0].click();", button)
    
    except:
        pass
    
    # We get the brands with a blank space in the name. This way we can exactly extract the brand and model for every car
    # (We consider model as the first word after the car brand)
    # We only do it once in the main page
    brands_list = driver.find_elements(By.CSS_SELECTOR, 'div[class="sui-ListTagcloud"]')[1].text.split('\n')
    
    brands_list = [x for x in brands_list if ' ' in x]
    
    #Creation and writing of csv file
    try:
        with open("scrapped_cnet.csv", 'w', newline='') as outfile:
    
            writer = csv.writer(outfile, delimiter=';')
    
            #Write header for each characteristic
            writer.writerow(["link",
                            "title",
                            "price",
                            "province",
                            "fuel",
                            "year",
                            "km",
                            "brand",
                            "model",
                            ])
    
            print("CSV File created, starting scrapping")
    
            page = 0
    
            while page < 8391:
                page = page + 1
    
                #Check recaptcha
                #If we find a captcha our script will solve it
                
                recaptchav2_solver(driver = driver)
    
                #Delay before starting scrolling
                time.sleep(random.uniform(1,3))
    
                #We call the scrolling function
                scroll_till_bottom(driver = driver)
                
                try:
                    for car in driver.find_elements(By.CSS_SELECTOR, 'div[data-ad-position]'):
                        try:
                            writer.writerow(extract_cars_info(car = car, brands_list = brands_list))
                        except:
                            print("Error scrapping one of the cars in" +str(driver.current_url))
                
                except:
                    print("Error in scrapping the car list in "+str(driver.current_url))
    
                #Click next page and proceed again
                click_next_page_button(driver = driver)
    
                if page%100 == 0:
                    print("Already scrapped",page,"pages")
                
                else:
                    pass
    
    except:
    #When we get an error we make a screenshot and also save HTML code into a .txt. This helps in troubleshooting
        print("Unhandled error in "+str(driver.current_url))
        driver.save_screenshot("error.png")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    
        with open('html_error.txt', 'wt', encoding='utf-8') as html_file:
            for line in soup.prettify():
                html_file.write(line)
                
    driver.quit()