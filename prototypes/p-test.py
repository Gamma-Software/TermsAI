from playwright.sync_api import sync_playwright
url = "https://openai.com/policies/terms-of-use"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url)
    print(page.title())
    page.screenshot(path="example.png")
    browser.close()
