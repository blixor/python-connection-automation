# LinkedIn Connection Scraper
# This script automates the process of fetching LinkedIn connections and their contact information
# It uses Selenium WebDriver with Firefox to navigate LinkedIn and extract data

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import NoSuchElementException        
from progress.bar import IncrementalBar
import time, csv, getpass

# Time to wait between scrolls to allow page content to load
SCROLL_PAUSE_TIME = 1.0

# Configure Firefox options for headless browsing
options = Options()
options.set_headless(headless = False)

# Configure Firefox capabilities for compatibility
capabilities = webdriver.DesiredCapabilities().FIREFOX
capabilities["marionette"] = True

# Configure Firefox profile to disable images for faster loading
firefox_profile = FirefoxProfile()
firefox_profile.set_preference('permissions.default.image', 2)

# Initialize the Firefox WebDriver with configured options
driver = webdriver.Firefox(firefox_options=options, firefox_profile=firefox_profile, capabilities=capabilities)

# LinkedIn credentials - replace with your credentials
username = ""
password = ""

# Login to LinkedIn
driver.get("https://www.linkedin.com")
driver.find_element_by_id('login-email').send_keys(username)
driver.find_element_by_id('login-password').send_keys(password)
driver.find_element_by_id('login-submit').click()

# Navigate to connections page
driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections")

# Get initial scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

# Scroll through the entire connections page to load all connections
while True:
    # Scroll to bottom of page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait for content to load
    time.sleep(SCROLL_PAUSE_TIME)

    # Check if we've reached the bottom of the page
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Find all connection cards on the page
cards = driver.find_elements_by_class_name('mn-connection-card__link')

# Extract profile links from connection cards
links = []
for card in cards:
    links.append(card.get_attribute('href'))

# Create CSV file to store connection information
with open("connections.csv","w", newline='') as csvfile:
    # Define CSV columns
    writer = csv.DictWriter(csvfile, fieldnames = ['Name', 'Headline', 'Location', 'Link', 'Website', 'Phone', 'Address', 'E-mail', 'Twitter'])
    writer.writeheader()

    # Initialize progress bar
    bar = IncrementalBar('Fetching Connections', max=len(links))

    # Process each connection's profile
    for link in links:
        # Navigate to contact info page
        driver.get(link + 'detail/contact-info')

        # Extract website information
        try:
            website = driver.find_element_by_class_name('ci-websites').find_element_by_class_name('pv-contact-info__contact-link').text
        except NoSuchElementException:
            website = ""

        # Extract phone number
        try:
            phone = driver.find_element_by_class_name('ci-phone').find_element_by_class_name('pv-contact-info__ci-container').find_element_by_tag_name('span').text
        except NoSuchElementException:
            phone = ""

        # Extract address
        try:
            address = driver.find_element_by_class_name('ci-address').find_element_by_class_name('pv-contact-info__contact-link').text
        except NoSuchElementException:
            address = ""

        # Extract email
        try:
            email = driver.find_element_by_class_name('ci-email').find_element_by_class_name('pv-contact-info__contact-link').text
        except NoSuchElementException:
            email = ""

        # Extract Twitter handle
        try:
            twitter = driver.find_element_by_class_name('ci-twitter').find_element_by_class_name('pv-contact-info__contact-link').text
        except NoSuchElementException:
            twitter = ""

        # Close contact info modal
        driver.find_element_by_class_name('artdeco-dismiss').click()

        # Extract basic profile information
        name = driver.find_element_by_class_name('pv-top-card-section__name').text
        
        # Extract headline
        try:
            headline = driver.find_element_by_class_name('pv-top-card-section__headline').text
        except NoSuchElementException:
            headline = ""

        # Extract location
        try:
            location = driver.find_element_by_class_name('pv-top-card-section__location').text
        except NoSuchElementException:
            location = ""

        # Write all collected information to CSV
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
        
        # Update progress bar and add small delay to avoid rate limiting
        bar.next()
        time.sleep(0.2)
    
    # Complete progress bar and close browser
    bar.finish()
    driver.close()
