import time
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # New import
from selenium.webdriver.support import expected_conditions as EC # New import

load_dotenv()
ROLL_NO = os.getenv("IMS_ROLL_NO")
PASSWORD = os.getenv("IMS_PASSWORD")

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
# Define a 'wait' object that we can reuse
wait = WebDriverWait(driver, 10)

try:
    driver.get("https://www.imsnsit.org/imsnsit/")
    
    # 1. Click Student Login
    login_link = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Student Login")))
    login_link.click()
    print("Clicked Student Login.")
    time.sleep(3)
    frames = driver.find_element(By.TAG_NAME, "frame")
    print(f"Total frames found: {len(frames)}")
    for idx, frame in enumerate(frames):
        print(f"Frame {idx} - Name: {frame.get_attribute('name')} | ID: {frame.get_attribute('id')}")
    # --- THE FRAME SWITCH (CRITICAL) ---
    # Many IMS portals put the login inside a frame. 
    # If it fails here, try searching your HTML for <frame name="...">
    try:
        # Check if a frame exists and switch to it. 
        # Common names are 'main', 'login', or 'top'.
        # If you don't know the name, we can try by index (0 is the first frame)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "main")))
        print("Switched to frame: 'main'")
    except:
        print("No frame 'main' found, staying in default content.")

    # 2. Find UID with Explicit Wait
    print("Looking for User ID field...")
    uid_input = wait.until(EC.presence_of_element_located((By.ID, "uid")))
    uid_input.send_keys(ROLL_NO)
    
    # 3. Find Password
    pwd_input = driver.find_element(By.ID, "pwd")
    pwd_input.send_keys(PASSWORD)
    
    print("Credentials entered successfully.")

except Exception as e:
    # This will help us see where it actually failed
    print(f"Failed at step: {e}")
    driver.save_screenshot("error_state.png")
    print("Saved 'error_state.png' for debugging.")

finally:
    time.sleep(5)
    driver.quit()