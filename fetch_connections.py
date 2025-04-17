# LinkedIn Connection Scraper
# Automates fetching LinkedIn connections and their contact details using Selenium
# Outputs data to a CSV file for easy analysis

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import NoSuchElementException        
from progress.bar import IncrementalBar
import time, csv, getpass

# Delay between scrolls to prevent rate limiting
SCROLL_PAUSE_TIME = 1.0

# Browser configuration
options = Options()
options.set_headless(headless = False)

# Firefox driver compatibility settings
capabilities = webdriver.DesiredCapabilities().FIREFOX
capabilities["marionette"] = True

# Optimize browser performance
firefox_profile = FirefoxProfile()
firefox_profile.set_preference('permissions.default.image', 2)  # Disable images

# Initialize browser with custom settings
driver = webdriver.Firefox(firefox_options=options, firefox_profile=firefox_profile, capabilities=capabilities)

# LinkedIn authentication
username = ""  # Add your LinkedIn email
password = ""  # Add your LinkedIn password

# Authenticate and navigate to connections page
driver.get("https://www.linkedin.com")
driver.find_element_by_id('login-email').send_keys(username)
driver.find_element_by_id('login-password').send_keys(password)
driver.find_element_by_id('login-submit').click()
driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections")

# Infinite scroll implementation
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Collect all connection profile URLs
cards = driver.find_elements_by_class_name('mn-connection-card__link')
links = []
for card in cards:
    links.append(card.get_attribute('href'))

# Export data to CSV
with open("connections.csv","w", newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = ['Name', 'Headline', 'Location', 'Link', 'Website', 'Phone', 'Address', 'E-mail', 'Twitter'])
    writer.writeheader()

    # Progress tracking
    bar = IncrementalBar('Fetching Connections', max=len(links))

    # Process each connection
    for link in links:
        # Fetch contact information
        driver.get(link + 'detail/contact-info')

        # Extract contact details with error handling
        try:
            website = driver.find_element_by_class_name('ci-websites').find_element_by_class_name('pv-contact-info__contact-link').text
        except NoSuchElementException:
            website = ""

        try:
            phone = driver.find_element_by_class_name('ci-phone').find_element_by_class_name('pv-contact-info__ci-container').find_element_by_tag_name('span').text
        except NoSuchElementException:
            phone = ""

        try:
            address = driver.find_element_by_class_name('ci-address').find_element_by_class_name('pv-contact-info__contact-link').text
        except NoSuchElementException:
            address = ""

        try:
            email = driver.find_element_by_class_name('ci-email').find_element_by_class_name('pv-contact-info__contact-link').text
        except NoSuchElementException:
            email = ""

        try:
            twitter = driver.find_element_by_class_name('ci-twitter').find_element_by_class_name('pv-contact-info__contact-link').text
        except NoSuchElementException:
            twitter = ""

        # Close contact modal and get profile info
        driver.find_element_by_class_name('artdeco-dismiss').click()
        name = driver.find_element_by_class_name('pv-top-card-section__name').text
        
        try:
            headline = driver.find_element_by_class_name('pv-top-card-section__headline').text
        except NoSuchElementException:
            headline = ""

        try:
            location = driver.find_element_by_class_name('pv-top-card-section__location').text
        except NoSuchElementException:
            location = ""

        # Save connection data
        writer.writerow({
            'Name': name, 
            'Headline': headline, 
            'Location': location, 
            'Link': link, 
            'Website': website, 
            'Phone': phone, 
            'Address': address, 
            'E-mail': email, 
            'Twitter': twitter
        })
        
        # Prevent rate limiting
        bar.next()
        time.sleep(0.2)
    
    # Cleanup
    bar.finish()
    driver.close()
