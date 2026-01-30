import time
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

ROLL_NO = os.getenv("IMS_ROLL_NO")
PASSWORD = os.getenv("IMS_PASSWORD")

if not ROLL_NO or not PASSWORD:
    print("❌ Error: IMS_ROLL_NO or IMS_PASSWORD not found in .env file!")
    exit()

print(f"👤 Using Roll No: {ROLL_NO[:3]}***")

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
driver.maximize_window()
wait = WebDriverWait(driver, 10)

try:
    # Step 1: Open main site
    print("🌐 Opening IMSNSIT...")
    driver.get("https://www.imsnsit.org/imsnsit/")
    
    # Step 2: Click Student Login
    print("🔘 Looking for Student Login link...")
    login_link = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Student Login")))
    login_link.click()
    print("✅ Clicked Student Login.")
    
    # Step 3: IMPORTANT - Wait longer for frames to fully load
    print("\n⏳ Waiting for page to fully load...")
    time.sleep(5)  # Give frames time to load their content
    
    # Step 4: Detect frames
    print("\n🔍 Checking for frames...")
    frames = driver.find_elements(By.TAG_NAME, "frame")
    print(f"Total frames found: {len(frames)}")
    
    for idx, frame in enumerate(frames):
        frame_name = frame.get_attribute('name')
        frame_src = frame.get_attribute('src')
        print(f"  Frame {idx}: Name='{frame_name}', Src='{frame_src}'")
    
    # Step 5: Try frame 0 first (banner - most likely has the form)
    print("\n🎯 Switching to 'banner' frame (frame 0)...")
    driver.switch_to.default_content()
    driver.switch_to.frame(0)
    
    # Wait a bit more for frame content to load
    time.sleep(2)
    
    # Step 6: Fill User ID
    print("\n📝 Entering User ID...")
    uid_input = wait.until(EC.presence_of_element_located((By.ID, "uid")))
    uid_input.clear()
    uid_input.send_keys(ROLL_NO)
    print("✅ User ID entered")
    
    # Step 7: Fill Password
    print("📝 Entering Password...")
    pwd_input = wait.until(EC.presence_of_element_located((By.ID, "pwd")))
    pwd_input.clear()
    pwd_input.send_keys(PASSWORD)
    print("✅ Password entered")
    
    # Step 8: Get CAPTCHA image info
    print("\n🖼️  CAPTCHA Details:")
    try:
        captcha_img = driver.find_element(By.ID, "captchaimg")
        captcha_src = captcha_img.get_attribute("src")
        print(f"  CAPTCHA image source: {captcha_src}")
        
        # Take screenshot
        driver.save_screenshot("captcha_screenshot.png")
        print("📸 Saved captcha_screenshot.png")
    except Exception as e:
        print(f"  ⚠️  Could not find CAPTCHA image: {e}")
    
    # Step 9: Manual CAPTCHA solving
    print("\n⚠️  === CAPTCHA REQUIRED ===")
    print("👀 Look at the browser window")
    print("📝 Type the CAPTCHA text you see:")
    captcha_text = input("Enter CAPTCHA: ")
    
    # Enter CAPTCHA
    print(f"📝 Entering CAPTCHA: {captcha_text}")
    captcha_input = driver.find_element(By.ID, "cap")
    captcha_input.clear()
    captcha_input.send_keys(captcha_text)
    print("✅ CAPTCHA entered")
    
    # Small delay to ensure everything is filled
    time.sleep(1)
    
    # Step 10: Click Login button
    print("\n🔐 Clicking Login button...")
    login_button = wait.until(EC.element_to_be_clickable((By.ID, "login")))
    login_button.click()
    print("✅ Login button clicked!")
    
    # Wait for navigation
    time.sleep(4)
    
    # Step 11: Switch back to default content to see the full page
    driver.switch_to.default_content()
    
    print(f"\n🎉 Current URL after login: {driver.current_url}")
    
    # Save the logged-in page
    with open("after_login.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("💾 Saved after_login.html")
    
    driver.save_screenshot("after_login.png")
    print("📸 Saved after_login.png")
    
    # Check if login was successful
    if "student.htm" in driver.current_url:
        print("\n⚠️  Still on login page - login may have failed!")
        print("Check error_state.png to see what happened")
    else:
        print("\n✅ LOGIN APPEARS SUCCESSFUL!")
    
    print("\n🔍 Browser will stay open. Look around the page.")
    print("Press Enter when you want to close...")
    input()

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print(f"Current URL: {driver.current_url}")
    
    # Try to get current frame info
    try:
        current_frame = driver.execute_script("return window.name")
        print(f"Current frame: {current_frame}")
    except:
        pass
    
    # Save debug info
    driver.save_screenshot("error_state.png")
    print("📸 Saved error_state.png")
    
    with open("error_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("💾 Saved error_page.html")

finally:
    print("\n👋 Closing browser in 5 seconds...")
    time.sleep(5)
    driver.quit()