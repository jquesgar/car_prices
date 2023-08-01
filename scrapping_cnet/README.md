# Credits
**Credits to theriley106 for the idea of using WhisperAI for captcha solving - https://github.com/theriley106/WhisperCaptcha/tree/main**

# Description
The `scrapping_cnet.py` is a Python script able to scrap car info and prices from car listings of a famous Spanish car listings website. (car model, brand, km, price, year...)

This web scrapping is based in `Selenium` using `Undetected Chromedriver`. It could be possible to scrap it via API scrapping POST request but I did not manage to configure it properly thus I got access denied. However it was a good exercise to use Selenium. Of course this solution could be implemented in `Puppeteer` or other similar solutions.

Two files are provided to do so: `recaptcha_solver.py` and `scrapping_cnet.py`. 

## `recaptcha_solver.py`
The script implements the nice solution proposed in (https://github.com/theriley106/WhisperCaptcha/tree/main) as a function `recaptchav2_solver`. 

A `main` function is provided to test its functionality. Regarding captcha solving, it is usually recommended to log with your google credentials to reduce the frequency of catpcha appearing. Also it enables the confirmation of 'Undetected Chromedriver` working as expected (if not, Google would detect our driver as a bot and won't let you to log in).

Regarding the original work, I added a new function to reload the captcha (sometimes our solver would not work). Even some times the audio version delivered is empty. This is why the `click_reload` function helps in debugging. Also, I changed the original `request_audio_version` funciton to match Spanish language for the iframe XPATH.

Finally, all functions are compiled in `recaptchav2_solver`. This function will try to solve the captcha up to 20 times. From the debugging I carried out, I added some conditions to detect the "captcha-solving state" and thus try to click the captcha reload button, refresh the webpage... 

## `scrapping_cnet.py`

This script includes the `recaptchav2_solver` function from the previous one. This will be called at the beggining of each page-scrapping-loop to solve a captcha if it is found. If not, it will pass.

Some functions are defined within the script:

- Since the website is dynamic some functions a function to scroll until the bottom of the webpage (`scroll_till_bottom`) was defined.
- Instead of performing a `GET` request the driver browses to the next page by clicking the next page button (`click_next_page_button`)
- Two other functions are defined to extract all the info from the cars listed (`extract_brand_and_model` & `extract_cars_info`).

The script basically:
1. Logs into the specified Google account and then browses to car listing website.
2. Once available, it will accept the website cookies prompt.
3. Then, it will extract a list with all the brands present in the car listing webpage. I had to do this because some car brands have spaces (e.g. *ALFA ROMEO*). Since we are generalizing the car model as the next word after the brand (e.g. *ALFA ROMEO Giulietta*) would give us `brand: ALFA` and `model: ROMEO`. By getting the `brand_list` we can extract the `brand` from the `title` and then make the next word the `model`. Therefore: `brand: ALFA ROMEO` and `model: Giulietta`.
4. Finally, the script will open a `.csv` file to store the scrapped data. A `while` loop (modifyable to the desired number of pages to scrap) will iterate to scrap each car listing page and write the data to the `.csv` file. After a new page is loaded, `recaptchav2_solver` will always check first is a captcha is available to be solved before proceeding to the car listing scrapping.

The script will finish after the specified pages are scrapped or if some exception is raised. If the last happens, a browser screenshot and `HTML` code will be stored in `.jpg` and `.txt` formats respectively for future debugging.

# Installation
A `cars_scrapping.yaml` is provided to create a conda environment with the packages and versions used. This environment is also valid for the `scrapping_ao` code.
