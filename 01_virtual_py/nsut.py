import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")

# FIX 1: Add a User-Agent so the site doesn't block the headless request
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# FIX 2: Ignore SSL errors (common for educational portals)
options.add_argument("--ignore-certificate-errors")
options.add_argument("--allow-running-insecure-content")

driver = webdriver.Chrome(options=options)

try:
    print("Navigating to site...")
    driver.get("https://www.imsnsit.org/imsnsit/")
    
    # FIX 3: Give the page a 5-second buffer to resolve redirects
    time.sleep(5) 
    
    actual_title = driver.title
    
    if actual_title:
        print("Success! Title:", actual_title)
    else:
        print("Title is empty. The page might still be loading or you were blocked.")
        # Debugging: Save a screenshot to see what the 'Headless' browser sees
        driver.save_screenshot("debug_view.png")
        print("Screenshot saved as debug_view.png")

finally:
    driver.quit()