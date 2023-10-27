import time
from bs4 import BeautifulSoup
from selenium import webdriver
url = "https://openai.com/policies/terms-of-use"
start_timer = time.time()

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.experimental_options['prefs'] = {
    'profile.managed_default_content_settings.images': 2
}
driver = webdriver.Chrome(options=options)
print("Page took {} seconds to load.".format(time.time() - start_timer))
driver.get(url)
print("Page took {} seconds to load.".format(time.time() - start_timer))

# Wait for the page to load and the dynamic content to render
# driver.implicitly_wait(20)
print("Page took {} seconds to load.".format(time.time() - start_timer))

# Get the HTML content of the webpage
html_content = driver.page_source

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")
print("Page took {} seconds to load.".format(time.time() - start_timer))
# Extract the text from the webpage
text = soup.get_text()
print("Page took {} seconds to load.".format(time.time() - start_timer))
# Print the extracted text
with open("insta.txt", "w") as file:
    file.write(text)
driver.save_screenshot('screenshot.png')
# Close the Selenium driver
driver.quit()
