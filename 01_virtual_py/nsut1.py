# scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def scrape_imsnsit_attendance(user_id, password):
    """
    Scrapes attendance from IMSNSIT portal
    """
    print("🚀 Starting IMSNSIT scraper...")
    
    # Setup Chrome
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    
    try:
        # Step 1: Go to main site
        print("📱 Opening IMSNSIT...")
        driver.get("https://www.imsnsit.org/imsnsit/")
        
        # Step 2: Click "Student Login" button
        print("🔘 Clicking Student Login...")
        student_login = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "student login"))
        )
        student_login.click()
        
        # Step 3: Wait for student.htm page to load
        time.sleep(2)
        print(f"📄 Current URL: {driver.current_url}")
        
        # Step 4: Fill in user_id (name="uid", id="uid")
        print("👤 Entering User ID...")
        user_id_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "uid"))
        )
        user_id_field.send_keys(user_id)
        
        # Step 5: Fill in password (id="pwd", name="pwd")
        print("🔒 Entering Password...")
        password_field = driver.find_element(By.ID, "pwd")
        password_field.send_keys(password)
        
        # Step 6: Handle CAPTCHA (if present)
        # Note: CAPTCHA requires manual input or OCR - for now we'll pause
        print("⚠️  If there's a CAPTCHA, solve it manually in the browser")
        print("⏸️  Press Enter here after solving CAPTCHA...")
        input()  # Wait for manual CAPTCHA solving
        
        # Step 7: Click Login button (id="login", name="login")
        print("🔑 Clicking Login...")
        login_button = driver.find_element(By.ID, "login")
        login_button.click()
        
        # Wait for page to load
        time.sleep(3)
        
        print(f"✅ Login successful! Current URL: {driver.current_url}")
        
        # Step 8: Now navigate to attendance
        # TODO: Add this in next step once you see the dashboard
        
        # Save the page source to analyze
        with open("after_login.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("💾 Saved page HTML to after_login.html")
        
        # Keep browser open to explore
        input("Press Enter to close browser...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        driver.save_screenshot("error_screenshot.png")
        print("📸 Saved error screenshot")
    
    finally:
        driver.quit()

# Test it!
if __name__ == "__main__":
    # Replace with your actual credentials
    user_id = input("Enter your User ID: ")
    password = input("Enter your Password: ")
    
    scrape_imsnsit_attendance(user_id, password)