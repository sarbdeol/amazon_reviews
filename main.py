import pandas as pd
import time
import requests
from bs4 import BeautifulSoup
import json,re
import csv
import os
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed
import openpyxl

from get_seller_detail import get_seller

from datetime import datetime,timedelta

def add_data_to_csv(data):
    # print(data)
    try:
        today_date = datetime.now().strftime('%Y%m%d')
        output_file_path = f'output_{today_date}.csv'
        # output_file_path = 'output.csv'
        fieldnames = ['Asin', 'Name', 'Number of Rating', 'Highest Number of Rating', 'Rating','Highest Rating', 'seller', 'Lowsest Price Among all seller', 'BSR', 'ProductUrl']
        
        # Check if the output file exists
        file_exists = os.path.exists(output_file_path)
        
        # Open the CSV file in append mode, create a new one if it doesn't exist
        with open(output_file_path, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # If the file doesn't exist, write the header row
            if not file_exists:
                writer.writeheader()
                
            # Write data to the CSV file
            writer.writerow(data)

        print("Data added successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
# Get the current working directory
current_directory = os.getcwd()

# API token for scrape.do
token = "2594e5d442b4457aa0e37b651200277726751d1e518"
def extract_asin_from_url(url):
    # Regular expression to find the ASIN in the URL
    pattern = r'/dp/([A-Z0-9]{10})'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        return None

# Function to get URL with token
def get_url(url):
    targetUrl = quote(url)
    proxy_url = "http://api.scrape.do?token={}&url={}&geoCode=us".format(token, targetUrl)
    return proxy_url
# Function to append data to an Excel file

count=0
def read_csv_file():
    data={}
    yesterday_date = datetime.now() - timedelta(days=1)
    yesterday_date_str = yesterday_date.strftime('%Y%m%d')

    # Construct the CSV file path with yesterday's date
    csv_file_path = f'output_{yesterday_date_str}.csv'
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Assuming ASIN is a column in the CSV file
            asin = row.get('Asin', None)
            if asin:
                data[asin] = row
    return data

def update_highest_number_rating(data, asin, new_number_of_ratings):
    if asin in data:
        old_number_of_ratings = data[asin].get('Highest Number of Rating', None)
        if old_number_of_ratings:
            # Extract numeric values from the strings
            new_rating_count = int(new_number_of_ratings.split()[0])
            old_rating_count = int(old_number_of_ratings.split()[0])
            # Compare and update 'Highest Number of Rating' if the new rating count is higher
            if new_rating_count > old_rating_count:
                data[asin]['Highest Number of Rating'] = new_number_of_ratings
        else:
            # If 'Highest Number of Rating' is not present, simply update it
            data[asin]['Highest Number of Rating'] = new_number_of_ratings
    else:
        print('Record with ASIN', asin, 'not found.')
def update_highest_rating(data, asin, new_number_of_ratings):
    if asin in data:
        old_number_of_ratings = data[asin].get('Highest Rating', None)
        if old_number_of_ratings:
            # Extract numeric values from the strings
            new_rating_count = float(new_number_of_ratings.split()[0])
            old_rating_count = float(old_number_of_ratings.split()[0])
            # Compare and update 'Highest Number of Rating' if the new rating count is higher
            if new_rating_count > old_rating_count:
                data[asin]['Highest Number of Rating'] = new_number_of_ratings
        else:
            # If 'Highest Number of Rating' is not present, simply update it
            data[asin]['Highest Number of Rating'] = new_number_of_ratings
    else:
        print('Record with ASIN', asin, 'not found.')
def scrape_amazon(url):
    global count
 
    count += 1
    # print(f'asin {count}:',url)
    product_url = url
    proxy_url = get_url(product_url)
    print(proxy_url)
    response = requests.get(proxy_url)
    if response.status_code == 200:
        try:
            data = read_csv_file()
        except:
            data={}
        asin = extract_asin_from_url(url)
        # print(data)
        if asin in data:
            print(f'{asin} found in csv')
            existing_data = data
            # print('existing_data', existing_data)
            # Update data with scraped information
            new_data = scrape_and_process_data(response,existing_data,asin)
            # print('new data', new_data)
            existing_data.update(new_data)
            data = existing_data
            # print(data)
            add_data_to_csv(data[asin])
        else:
            result = scrape_and_process_data(response,None,asin)
            # print(result)
            add_data_to_csv(result)
            
def scrape_and_process_data(response,data_from_csv,asin):
        data={}
        soup = BeautifulSoup(response.content, 'html.parser')
        
        data['Asin']=asin
        try:
            title_element = soup.find('span', id='productTitle')
            title = title_element.get_text(strip=True).strip()
            data['Name']=title
        except:
            data['Name']= ''
    
        try:
            reviews_element = soup.find('span', id='acrCustomerReviewText')
            CustomerReview = reviews_element.get_text(strip=True)
            data['Number of Rating']=CustomerReview
        except:

            data['Number of Rating'] = ''

        
        # Read CSV file and store data
        
        try:
            update_highest_number_rating(data_from_csv, asin, data['Number of Rating'])      
        except:
            data['Highest Number of Rating']=data['Number of Rating']
        try:
            rating_element = soup.find('span', class_='reviewCountTextLinkedHistogram')
            StarRating = rating_element['title'].split('out')[0]
            data['Rating']=StarRating
            
        except:
            data['Rating']=''
  
        try:
            update_highest_rating(data_from_csv, asin, data['Rating'])      
        except:
            data['Highest Rating']=data['Rating']
        try:
            seller_link = soup.find('span', {'data-action': 'show-all-offers-display'}).find('a')['href']
            print(seller_link)
            seller_url = f'https://www.amazon.com{seller_link}'
            seller_info=get_seller(seller_url)
                    # seller_info.append(seller_detail)
            data['seller']=seller_info
        except:
            data['seller']=''
        try:
            price_whole_span = soup.find('span', class_='a-price-whole')
            price_fraction_span = soup.find('span', class_='a-price-fraction')
            # Get the text from the price_whole_span and price_fraction_span
            price = price_whole_span.get_text(strip=True).replace('.', '') + '.' + price_fraction_span.get_text(strip=True)
            data['Lowsest Price Among all seller']=price

        except:
            data['Lowsest Price Among all seller']=''
    # print('sellerrank1, sellerrank2, sellerrank3',sellerrank1, sellerrank2, sellerrank3)
    
        # Extract Best Sellers Rank
        best_sellers_rank_span = soup.find('span', string=' Best Sellers Rank: ')
        if best_sellers_rank_span:
            # Extract the text containing the rank
            rank_text = best_sellers_rank_span.next_sibling.strip()

            # Extract only the numerical value from the rank text
            BSR = ''.join(filter(str.isdigit, rank_text))
            data['BSR']=BSR
            
        else:
            data['BSR']=''
        # Find the canonical link tag
        canonical_link = soup.find('link', rel='canonical')

        # Extract the href attribute value if the canonical link tag exists
        if canonical_link:
            ProductUrl = canonical_link.get('href')
            data['ProductUrl']=ProductUrl
        else:
            data['ProductUrl']=ProductUrl
        # print('ProductUrl',ProductUrl)
    

    
       
    
        
        return data
            
            

          

import csv

def read_urls_from_csv(file_path):
    urls = []
    with open(file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            # Assuming the URL is in the first column of each row
            urls.append(row[0])
    return urls

# Example usage:
file_path = 'input.csv'  # Replace 'urls.csv' with the path to your CSV file
urls = read_urls_from_csv(file_path)
# print(urls)

for url in urls:
    scrape_amazon(url)
    
    
            

