from bs4 import BeautifulSoup

def extract_seller_info(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract Best Sellers Rank
    best_sellers_rank_span = soup.find('span', class_='a-text-bold', string=' Best Sellers Rank ')
    if best_sellers_rank_span:
        # Extract the text containing the Best Sellers Rank
        best_sellers_rank_text = best_sellers_rank_span.find_next_sibling('ul').find('li').get_text(strip=True)
    else:
        best_sellers_rank_text = None
    
    # Extract Seller Information
    seller_info = []
    seller_ul = soup.find('ul', class_='a-unordered-list', attrs={'class': 'a-nostyle', 'class': 'a-vertical', 'class': 'zg_hrsr'})
    if seller_ul:
        seller_li_items = seller_ul.find_all('li')
        for li in seller_li_items:
            seller_name = li.find('span', class_='a-list-item').find('a').get_text(strip=True).strip()
            print(seller_name)
            seller_ratings = int(li.find('span', class_='a-list-item').get_text(strip=True).split('#')[1].strip().split()[0].replace(',', ''))
            
            # Extract Seller Price if available
            seller_price_text = li.find('span', class_='a-list-item').get_text(strip=True)
            seller_price_index = seller_price_text.find('$')
            if seller_price_index != -1:  # Check if '$' is found
                seller_price = float(seller_price_text[seller_price_index + 1:].strip().split()[0])
            else:
                seller_price = None
            
            # Extract Ship From if available
            ship_from_index = seller_price_text.find('from ')
            if ship_from_index != -1:  # Check if 'from ' is found
                ship_from = seller_price_text[ship_from_index + 5:].strip()
            else:
                ship_from = None

            seller_detail = {
                "Seller_Name": seller_name,
                "Seller_Ratings": seller_ratings,
                "Seller_Price": seller_price,
                "Ship_From": ship_from
            }
            seller_info.append(seller_detail)

    return best_sellers_rank_text, seller_info

# Example HTML snippet
html_snippet = '''
<span class="a-list-item">
    <span class="a-text-bold"> Best Sellers Rank: </span> 
    #61,761 in Books (<a href="/gp/bestsellers/books/ref=pd_zg_ts_books">See Top 100 in Books</a>) 
    <ul class="a-unordered-list a-nostyle a-vertical zg_hrsr">  
        <li><span class="a-list-item"> #3 in <a href="/gp/bestsellers/books/227644/ref=pd_zg_hrsr_books">Nursing Home &amp; Community Health</a></span></li>  
        <li><span class="a-list-item"> #64 in <a href="/gp/bestsellers/books/227627/ref=pd_zg_hrsr_books">Medical Test Preparation &amp; Review</a></span></li>  
        <li><span class="a-list-item"> #88 in <a href="/gp/bestsellers/books/227665/ref=pd_zg_hrsr_books">Nursing Reviews &amp; Study Guides (Books)</a></span></li>  
    </ul>    
</span>
'''

# Extract seller information from HTML snippet
best_sellers_rank, seller_info = extract_seller_info(html_snippet)
print("Best Sellers Rank:", best_sellers_rank)
print("Seller Information:")
for seller in seller_info:
    print(seller)
