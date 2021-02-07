import json 
import unidecode
import requests
from selenium import webdriver  
from selenium.webdriver.common.by import By  
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from datetime import datetime
from bs4 import BeautifulSoup

startTime = datetime.now()

def remove_attributes(html):
    """
    docstring
    """
    REMOVE_ATTRIBUTES = ['lang','language','onmouseover','onmouseout','script','style','font',
                        'dir','face','size','color','style','class','width','height','hspace',
                        'border','valign','align','background','bgcolor','text','link','vlink',
                        'alink','cellpadding','cellspacing', 'id']

    soup = BeautifulSoup(html)
    for tag in soup():        
        for attribute in REMOVE_ATTRIBUTES:
            del tag[attribute]
    return str(soup)

def get_images(soup):
    image_list = []
    images = soup.find_all('img')
    for image in images:
        if 'src' in image:
            image_list.append(image['src'])
    
    return image_list

def get_content(driver, link):
    driver.implicitly_wait(3)
    product = {}  
    products = [] 
    driver.execute_script("window.scrollTo(0, 800)") 
    while True:
        try:
        # Define an element that you can start scraping when it appears
        # If the element appears after 5 seconds, break the loop and continue
            # product_id = WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table.purchaseCoinTable td.item"))).get_attribute("innerHTML")
            product_table = WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table.purchaseCoinTable")))
            break
        except TimeoutException:
            # If the loading took too long, print message and try again
            print("Loading took too much time!")
            driver.refresh()
            driver.save_screenshot(f'screenshot_error-{datetime.now().strftime("%Y%m%d-%H%M%S")}.png')

    table = driver.find_element_by_css_selector('table.purchaseCoinTable')
    rows = table.find_elements(By.TAG_NAME, "tr")
    row_count = len(rows)
    count = 1
    # import pdb; pdb.set_trace()
    if row_count == 4:
        for row in rows:
            if count == 1:
                pass 
            elif count > 2:
                pass
            else:
                col = row.find_elements(By.TAG_NAME, "td")            
                table_product = {
                    'name': col[1].text,
                    'product_id': col[2].text,
                    'price': col[3].text,
                    'status': 'Available' if col[4].text == '' else col[4].text,
                }  
                products.append(table_product) 
            count+=1 
    else:
        for row in rows:
            if count != 1 and count < row_count-2:
                col = row.find_elements(By.TAG_NAME, "td")            
                table_product = {
                    'name': col[1].text,
                    'product_id': col[2].text,
                    'price': 'NOT DEFINED' if col[3].text == '' else col[3].text,
                    'status': 'Available' if col[4].text == '' else col[4].text,
                }  
                products.append(table_product) 
            count+=1                                  
    
    
    # import pdb; pdb.set_trace()    
    heading = driver.find_element_by_css_selector('h1.Heading').get_attribute("innerHTML").replace("\n", "")
    key = heading.replace(" ", "_").replace("\n", "").lower()
    description = driver.find_element_by_css_selector('span#ctlProductDetail_lblSummary').get_attribute("innerHTML").replace("\n", "").replace("    ", "").replace("<p>&nbsp;</p>", "").replace("<span>", "").replace("</span>", "").replace("<p><span></span></p>", "").replace("<p></p><p></p><p></p>", "").replace("<font>", "").replace("</font>", "").replace(u'\xa0', u' ').replace("&nbsp;", " ")

    description_images = BeautifulSoup(description, "html.parser")
    description_images = get_images(description_images)


    details = driver.find_element_by_css_selector('div#details').get_attribute("innerHTML").replace("\n", "").replace("<b><p></p></b><p></p><p></p>", "").replace("<p></p><p></p><p></p>", "").replace("<p>&nbsp;</p>", "").replace("<b><p></p></b>", "").replace("<p></p>", "").replace("<p><b></b></p>", "").replace(u"\u00a0", "").replace("<span>", "").replace("</span>", "").replace("<font>", "").replace("</font>", "").replace(u'\xa0', u' ').replace("&nbsp;", " ")

    details_images = BeautifulSoup(details, "html.parser")
    details_images = get_images(details_images)

    specifications = driver.find_element_by_css_selector('div#specifications').get_attribute("innerHTML").replace("\n", "").replace(u"\u00a0", "").replace("<span>", "").replace("</span>", "").replace("<font>", "").replace("</font>", "").replace(u'\xa0', u' ').replace("&nbsp;", " ")
    series = driver.find_element_by_css_selector('div#series').get_attribute("innerHTML").replace("\n", "").replace(u"\u00a0", "").replace("<span>", "").replace("</span>", "").replace("<font>", "").replace("</font>", "").replace(u'\xa0', u' ').replace("&nbsp;", " ")
    
    meta_description = driver.find_elements_by_css_selector("meta[name='description']")
    if len(meta_description) > 0:
        meta_description = unidecode.unidecode(meta_description[0].get_attribute('content')).replace("\n", "").replace("    ", "")
    meta_keywords = driver.find_elements_by_css_selector("meta[name='keywords']")
    if len(meta_keywords) > 0:
        meta_keywords = unidecode.unidecode(meta_keywords[0].get_attribute('content')).replace("\n", "")
        

    product[key] = []
    product[key].append({
        'url': link,
        'products': products,
        'heading':unidecode.unidecode(heading),
        'description':remove_attributes(unidecode.unidecode(description)),
        'desctiption_images': description_images,
        'details':remove_attributes(unidecode.unidecode(details)),
        'details_images': details_images,
        'series':remove_attributes(unidecode.unidecode(series)),
        'meta_description':meta_description,
        'meta_keywords':meta_keywords,
    })   

    print(f"{product}\n")
    return product 


chrome_options = Options()  
chrome_options.add_argument("--headless")  
driver = webdriver.Chrome(options=chrome_options)

master_hrefs = []
master_products = []

for x in range(1, 51):
    driver.get(f"https://www.perthmint.com/catalogue/default.aspx?Page={x}")
    print(f"getting url: https://www.perthmint.com/catalogue/default.aspx?Page={x}")
    hrefs = driver.find_elements_by_css_selector("#centreColumn div.coinShortDescription a")
    
    for link in hrefs: 
        master_hrefs.append(link.get_attribute('href'))


total = len(master_hrefs)

for link in master_hrefs:     
    print(f"{total} {link}")     
    r = requests.get(link)
    # print(f"1: {r.status_code}")
    if r.status_code == 200:
        total = total-1 
        driver.get(link)
        product = get_content(driver, link)
    else:
        r = requests.get(link)
        print(f"2: {r.status_code}")
        if r.status_code == 200:
            total = total-1 
            driver.get(link)
            product = get_content(driver, link)

    master_products.append(product)

driver.quit()


with open(f'products-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json', 'w') as outfile:
    json.dump(master_products, outfile)

#Python 3: 
print(datetime.now() - startTime)






