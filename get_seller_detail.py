from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.service import Service

def get_seller(url):
    # Initialize the WebDriver
    options=webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    chrome_driver_path = '/usr/bin/chromedriver'
    service = Service(chrome_driver_path)

    # Initialize WebDriver
    driver = webdriver.Chrome(service=service, options=options) # Or specify the path to your webdriver
    # Load the webpage
    driver.get(url)
    time.sleep(2)
    # Find all offer elements
    try:
        offer_elements = driver.find_elements(By.XPATH, '//*[@id="aod-offer"]')
        # print(len(offer_elements))
        see_more=driver.find_element(By.XPATH,'//*[@id="aod-pinned-offer-show-more-link"]')

        see_more.click()
        time.sleep(1)
        # Define a list to store all seller details
        all_seller_details = []

        # Iterate over each offer element
        for offer_element in offer_elements:
            # Extract seller details
            seller_name = offer_element.find_element(By.XPATH, './/div/a[@class="a-size-small a-link-normal"]').text
            seller_ratings = offer_element.find_element(By.ID, 'seller-rating-count-{iter}').text.split('ratings')[0].replace('(','').strip()
            seller_price = offer_element.find_element(By.XPATH, './/*[@class="a-price aok-align-center centralizedApexPricePriceToPayMargin"]').text.replace('\n','.')
            ship_from = offer_element.find_element(By.XPATH, './/span[@class="a-size-small a-color-base"]').text

            # Append the seller details to the list
            seller_detail = {
                "Seller_Name": seller_name,
                "Seller_Ratings": seller_ratings,
                "Seller_Price": seller_price,
                "Ship_From": ship_from
            }
            all_seller_details.append(seller_detail)

        # Close the WebDriver
        driver.quit()
        print(all_seller_details)
        return all_seller_details
    except Exception as e:
        print(e)
        return None
    # # Print all seller details
    # for idx, seller_detail in enumerate(all_seller_details, start=1):
    #     print(f"Seller {idx}:")
    #     print(seller_detail)


get_seller('https://amazon.com/gp/offer-listing/B0CTX46384/ref=aod_pop_null_new_olp_sr?ie=UTF8&condition=new_olp')