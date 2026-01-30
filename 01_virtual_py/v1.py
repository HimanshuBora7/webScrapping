# Import the main webdriver module to control the browser
from selenium import webdriver

# Import Options to customize browser behavior (like headless mode or window size)
from selenium.webdriver.chrome.options import Options

# Import 'By' to specify how to locate elements (ID, Name, Class, etc.)
from selenium.webdriver.common.by import By

# Import 'Keys' to simulate keyboard actions like ENTER, TAB, or BACKSPACE
from selenium.webdriver.common.keys import Keys

# Import 'time' to use sleep, which pauses the script for a set number of seconds
import time 

# --- STEP 1: CONFIGURE BROWSER SETTINGS ---
options = Options()

# Security and memory flags required for stable operation on Linux
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Comment out Headless to see the browser window physically open on your screen
# options.add_argument("--headless")

# --- STEP 2: INITIALIZE THE DRIVER ---
# Selenium Manager handles the driver download and version matching automatically
driver = webdriver.Chrome(options=options)

# --- STEP 3: THE ACTION (Wrapped in Try/Finally) ---
try:
    # 1. Open Google
    driver.get("https://google.com")
    
    # 2. Find the search input element. 
    # 'q' is the unique name attribute Google uses for its search bar.
    # Using By.NAME is much more reliable than using long random class names.
    search_bar = driver.find_element(By.NAME, "q")
    
    # 3. Type the query into the search bar
    search_bar.send_keys("game of thrones")
    
    # 4. Simulate pressing the 'Enter' key to start the search
    search_bar.send_keys(Keys.ENTER)
    
    # 5. Brief pause to let the results page load its title
    time.sleep(2)
    print("Success! The page title is now:", driver.title)
    
    # 6. Keep the browser open for 100 seconds so you can see the results
    print("Holding browser open for 100 seconds...")
    time.sleep(100)

except Exception as e:
    # If the code crashes (e.g., can't find the search bar), this prints why
    print(f"An error occurred: {e}")

finally:
    # Close the browser session and free up system memory.
    # If you want to keep the window open after the script ends, 
    # you can temporarily comment this line out.
    driver.quit()
    print("Browser closed.")