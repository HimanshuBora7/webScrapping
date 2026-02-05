import time
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

load_dotenv()

ROLL_NO = os.getenv("IMS_ROLL_NO")
PASSWORD = os.getenv("IMS_PASSWORD")

if not ROLL_NO or not PASSWORD:
    print("❌ Error: Credentials not found in .env!")
    exit()

print(f"👤 Using Roll No: {ROLL_NO[:3]}***")

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
driver.maximize_window()
wait = WebDriverWait(driver, 10)


def find_and_click_link(driver, keywords, frame_names=['data', 'top', 'contents', 'bottom', 'banner'], exact_match=False):
    """Helper to find and click a link across multiple frames"""
    # First try main content (no frame)
    try:
        driver.switch_to.default_content()
        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            # Get text including nested elements like <b>
            link_text = link.text.strip()
            link_html = link.get_attribute('innerHTML') or ""
            
            if exact_match:
                if link_text in keywords or any(keyword in link_html for keyword in keywords):
                    print(f"✅ Found '{link.text}' in main content!")
                    link.click()
                    return True
            else:
                if any(keyword.lower() in link_text.lower() for keyword in keywords):
                    print(f"✅ Found '{link.text}' in main content!")
                    link.click()
                    return True
    except Exception as e:
        pass
    
    # Then try frames
    for frame_name in frame_names:
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(frame_name)
            
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                link_text = link.text.strip()
                link_html = link.get_attribute('innerHTML') or ""
                
                if exact_match:
                    if link_text in keywords or any(keyword in link_html for keyword in keywords):
                        print(f"✅ Found '{link.text}' in {frame_name}!")
                        link.click()
                        return True
                else:
                    if any(keyword.lower() in link_text.lower() for keyword in keywords):
                        print(f"✅ Found '{link.text}' in {frame_name}!")
                        link.click()
                        return True
        except Exception as e:
            continue
    return False


def extract_attendance_table(html):
    """Parse IMS attendance HTML and extract structured data"""
    import re
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find the main attendance table
    tables = soup.find_all('table')
    
    attendance_data = []
    subject_names = {}
    
    for table in tables:
        # Look for the header row with subject codes
        header_row = None
        for row in table.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            
            # This is the header row with subject codes
            if 'Days' in cell_texts or any('0603' in text or '0601' in text or '0602' in text for text in cell_texts):
                header_row = cell_texts
                break
        
        if not header_row:
            continue
        
        # Extract subject codes (skip the "Days" column)
        subject_codes = [code for code in header_row[1:] if code and code != 'Days']
        
        # Now find the summary rows
        for row in table.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            
            if len(cells) == 0:
                continue
            
            first_cell = cells[0].get_text(strip=True)
            
            # Overall (%) row - this is what we want!
            if 'Overall (%)' in first_cell or 'Overall%' in first_cell:
                percentages = [cell.get_text(strip=True) for cell in cells[1:]]
                
                for i, subject_code in enumerate(subject_codes):
                    if i < len(percentages):
                        attendance_data.append({
                            'Subject Code': subject_code,
                            'Attendance %': percentages[i]
                        })
            
            # Get total classes
            elif 'Overall Class' in first_cell or 'Total Classes' in first_cell:
                totals = [cell.get_text(strip=True) for cell in cells[1:]]
                for i, subject_code in enumerate(subject_codes):
                    if i < len(totals) and i < len(attendance_data):
                        attendance_data[i]['Total Classes'] = totals[i]
            
            # Get present count
            elif 'Overall' in first_cell and 'Present' in first_cell:
                presents = [cell.get_text(strip=True) for cell in cells[1:]]
                for i, subject_code in enumerate(subject_codes):
                    if i < len(presents) and i < len(attendance_data):
                        attendance_data[i]['Classes Present'] = presents[i]
            
            # Get absent count  
            elif 'Overall' in first_cell and 'Absent' in first_cell:
                absents = [cell.get_text(strip=True) for cell in cells[1:]]
                for i, subject_code in enumerate(subject_codes):
                    if i < len(absents) and i < len(attendance_data):
                        attendance_data[i]['Classes Absent'] = absents[i]
    
    # Extract subject names using regex - look for pattern "CODE-Name"
    full_html = str(soup)
    
    # Pattern: Subject code followed by dash and name
    for code in subject_codes:
        # Look for patterns like "ITITC601-Web Technology"
        pattern = rf'{code}-([^<\n]+?)(?:<br>|<|$)'
        match = re.search(pattern, full_html, re.IGNORECASE)
        
        if match:
            name = match.group(1).strip()
            # Clean up any extra text
            name = re.sub(r'---?>.*$', '', name).strip()
            subject_names[code] = name
    
    # Add full names to attendance data
    for item in attendance_data:
        code = item['Subject Code']
        if code in subject_names:
            item['Subject Name'] = subject_names[code]
    
    return attendance_data


try:
    # Step 1: Login
    print("🌐 Opening IMSNSIT...")
    driver.get("https://www.imsnsit.org/imsnsit/")
    
    print("🔘 Clicking Student Login...")
    login_link = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Student Login")))
    login_link.click()
    time.sleep(5)
    
    # Step 2: Fill login form
    print("📝 Filling login form...")
    driver.switch_to.frame(0)
    
    uid_input = wait.until(EC.presence_of_element_located((By.ID, "uid")))
    uid_input.send_keys(ROLL_NO)
    
    pwd_input = driver.find_element(By.ID, "pwd")
    pwd_input.send_keys(PASSWORD)
    
    print("\n⚠️  Solve CAPTCHA in browser")
    captcha_text = input("Enter CAPTCHA: ")
    
    captcha_input = driver.find_element(By.ID, "cap")
    captcha_input.send_keys(captcha_text)
    
    login_button = driver.find_element(By.ID, "login")
    login_button.click()
    
    print("⏳ Waiting for dashboard...")
    time.sleep(8)
    
    driver.switch_to.default_content()
    print("✅ Logged in!\n")
    
    # Step 3: Navigate to My Activities
    print("🔍 Looking for 'My Activities'...")
    
    if find_and_click_link(driver, ['My Activities'], exact_match=True):
        print("🎉 Clicked 'My Activities'!")
        time.sleep(5)
    else:
        print("❌ Couldn't find 'My Activities' automatically")
        print("Please click it manually, then press Enter...")
        input()
    
    # Step 4: Click "Attendance" tab/section
    print("\n🔍 Looking for 'Attendance' tab...")
    
    if find_and_click_link(driver, ['ATTENDANCE', 'Attendance'], exact_match=True):
        print("🎉 Clicked 'Attendance' tab!")
        time.sleep(5)
    else:
        # Try partial match as backup
        if find_and_click_link(driver, ['attendance', 'attend']):
            print("🎉 Clicked 'Attendance'!")
            time.sleep(5)
        else:
            print("⚠️  'Attendance' tab not found automatically")
            print("Please click it manually, then press Enter...")
            input()
    
    # Step 5: Click "My Attendance" option
    print("\n🔍 Looking for 'My Attendance' option...")
    
    if find_and_click_link(driver, ['My Attendance'], exact_match=True):
        print("🎉 Clicked 'My Attendance'!")
        time.sleep(5)
    else:
        print("⚠️  'My Attendance' not found automatically")
        print("Please click it manually, then press Enter...")
        input()
    
    # Step 6: Select Year and Semester
    print("\n📅 Looking for Year/Semester dropdowns...")
    
    from selenium.webdriver.support.ui import Select
    
    year_selected = False
    semester_selected = False
    
    for frame_name in ['data', 'contents', 'bottom', 'top']:
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(frame_name)
            
            # Find all select elements
            selects = driver.find_elements(By.TAG_NAME, "select")
            
            for select_elem in selects:
                select = Select(select_elem)
                
                # Get the name/id to identify what this dropdown is
                select_name = select_elem.get_attribute("name") or select_elem.get_attribute("id") or ""
                
                # Check options to determine if it's year or semester
                options_text = [opt.text.lower() for opt in select.options]
                
                # Year dropdown (usually has values like 2024, 2023, etc. or 1st Year, 2nd Year)
                if not year_selected and any(keyword in select_name.lower() for keyword in ['year', 'yr']):
                    print(f"\n📋 Found Year dropdown in {frame_name}:")
                    for i, opt in enumerate(select.options):
                        print(f"  [{i}] {opt.text}")
                    
                    year_choice = input("Enter the NUMBER in brackets (e.g., 1 for 2025-26): ")
                    select.select_by_index(int(year_choice))
                    print(f"✅ Selected: {select.options[int(year_choice)].text}")
                    year_selected = True
                    time.sleep(1)
                
                # Semester dropdown (usually has Semester 1, Semester 2, etc.)
                elif not semester_selected and any(keyword in select_name.lower() for keyword in ['sem', 'semester']):
                    print(f"\n📋 Found Semester dropdown in {frame_name}:")
                    for i, opt in enumerate(select.options):
                        print(f"  [{i}] {opt.text}")
                    
                    sem_choice = input("Enter the NUMBER in brackets: ")
                    select.select_by_index(int(sem_choice))
                    print(f"✅ Selected: {select.options[int(sem_choice)].text}")
                    semester_selected = True
                    time.sleep(1)
            
            # If we found both dropdowns in this frame, look for submit button
            if year_selected and semester_selected:
                print(f"\n🔍 Looking for Submit button in {frame_name}...")
                
                # Try to find submit button - avoid PDF download button
                buttons = driver.find_elements(By.TAG_NAME, "input") + driver.find_elements(By.TAG_NAME, "button")
                
                for button in buttons:
                    button_type = button.get_attribute("type") or ""
                    button_value = (button.get_attribute("value") or button.text or "").lower()
                    button_name = (button.get_attribute("name") or "").lower()
                    
                    # Skip PDF and other unwanted buttons
                    if 'pdf' in button_value or 'download' in button_value or 'mpdfx' in button_name:
                        continue
                    
                    # Look for submit button
                    if (button_type.lower() == "submit" and button_name == "submit") or button_value == "submit":
                        print(f"✅ Found Submit button!")
                        button.click()
                        print("🎉 Clicked Submit!")
                        time.sleep(5)
                        break
                
                break  # Exit frame loop once we've submitted
                
        except Exception as e:
            continue
    
    if not year_selected or not semester_selected:
        print("\n⚠️  Couldn't find dropdowns automatically")
        print("Please select Year, Semester and click Submit manually")
        input("Press Enter once you've submitted...")
    
    # Step 7: Extract attendance data from all frames
    print("\n📊 Extracting attendance data...")
    
    all_attendance = []
    
    for frame_name in ['data', 'contents', 'bottom', 'top']:
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(frame_name)
            
            html = driver.page_source
            
            # Check if this frame has attendance data
            if 'attend' in html.lower() and len(html) > 500:
                print(f"\n✅ Found data in '{frame_name}' frame!")
                
                # Save raw HTML
                with open(f"attendance_{frame_name}.html", "w", encoding="utf-8") as f:
                    f.write(html)
                
                # Screenshot
                driver.save_screenshot(f"attendance_{frame_name}.png")
                
                # Try to parse structured data
                attendance_rows = extract_attendance_table(html)
                if attendance_rows:
                    print(f"📋 Extracted {len(attendance_rows)} subjects")
                    all_attendance.extend(attendance_rows)
                    
                    # Preview
                    for row in attendance_rows[:3]:
                        print(f"   {row}")
                
        except Exception as e:
            continue
    
    # Save structured data
    if all_attendance:
        df = pd.DataFrame(all_attendance)
        
        # Reorder columns for better readability
        cols = ['Subject Code', 'Subject Name', 'Classes Present', 'Classes Absent', 'Total Classes', 'Attendance %']
        df = df[[col for col in cols if col in df.columns]]
        
        df.to_csv("attendance_data.csv", index=False)
        print(f"\n💾 Saved structured data to attendance_data.csv")
        
        print("\n📊 YOUR ATTENDANCE SUMMARY:")
        print("="*80)
        for _, row in df.iterrows():
            print(f"\n🎓 {row.get('Subject Code', 'N/A')} - {row.get('Subject Name', 'N/A')}")
            print(f"   Present: {row.get('Classes Present', 'N/A')}/{row.get('Total Classes', 'N/A')} classes")
            print(f"   Attendance: {row.get('Attendance %', 'N/A')}")
        print("\n" + "="*80)
    else:
        print("\n⚠️  No structured data extracted - check HTML files manually")
    
    print("\n" + "="*60)
    print("✅ Scraping complete!")
    print("="*60)
    print("\n📁 Files created:")
    print("  - attendance_*.html (raw HTML)")
    print("  - attendance_*.png (screenshots)")
    if all_attendance:
        print("  - attendance_data.csv (structured data)")
    
    print("\n🔍 Browser staying open for manual inspection")
    print("Press Enter to close...")
    input()

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    driver.save_screenshot("error.png")

finally:
    driver.quit()