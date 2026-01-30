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
import re

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


def find_and_expand_tree_node(driver, text_keywords, frame_names=['data', 'top', 'contents', 'bottom', 'banner']):
    """Find a tree node and click its expandable hitarea to expand it"""
    print(f"🔍 Looking for expandable tree node containing: {text_keywords}")
    
    for frame_name in frame_names:
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(frame_name)
            
            # Strategy 1: Find by looking for text near hitarea
            elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Attendance') or contains(text(), 'ATTENDANCE')]")
            
            for elem in elements:
                try:
                    parent = elem.find_element(By.XPATH, "./..")
                    hitareas = parent.find_elements(By.CLASS_NAME, "hitarea")
                    
                    for hitarea in hitareas:
                        classes = hitarea.get_attribute("class") or ""
                        if "expandable-hitarea" in classes or "collapsable-hitarea" in classes:
                            print(f"✅ Found expandable tree node in '{frame_name}' frame!")
                            hitarea.click()
                            time.sleep(2)
                            driver.switch_to.default_content()
                            return True
                except:
                    continue
            
            # Strategy 2: Find all hitareas and click the expandable ones
            hitareas = driver.find_elements(By.CLASS_NAME, "hitarea")
            
            for hitarea in hitareas:
                classes = hitarea.get_attribute("class") or ""
                
                if "expandable-hitarea" in classes:
                    try:
                        parent = hitarea.find_element(By.XPATH, "./..")
                        text = parent.text.strip()
                        
                        if any(keyword.lower() in text.lower() for keyword in text_keywords):
                            print(f"✅ Found expandable '{text}' in '{frame_name}' frame!")
                            hitarea.click()
                            time.sleep(2)
                            driver.switch_to.default_content()
                            return True
                    except:
                        continue
                        
        except Exception as e:
            continue
    
    driver.switch_to.default_content()
    return False


def find_and_click_link(driver, keywords, frame_names=['data', 'top', 'contents', 'bottom', 'banner'], exact_match=False):
    """Helper to find and click a link across multiple frames"""
    try:
        driver.switch_to.default_content()
        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links:
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


def extract_attendance_table_enhanced(html, debug=True):
    """
    Enhanced attendance table parser with better debugging
    Handles various IMS table formats
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    if debug:
        print("\n" + "="*80)
        print("🔍 DEBUG: Analyzing HTML structure")
        print("="*80)
    
    # Find all tables
    tables = soup.find_all('table')
    if debug:
        print(f"\n📊 Found {len(tables)} table(s) in HTML")
    
    attendance_data = []
    subject_names = {}
    
    for table_idx, table in enumerate(tables):
        if debug:
            print(f"\n--- Analyzing Table {table_idx + 1} ---")
        
        rows = table.find_all('tr')
        if debug:
            print(f"   Rows: {len(rows)}")
        
        # Try to find header row with subject codes
        header_row = None
        header_row_idx = -1
        
        for row_idx, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            
            if debug and row_idx < 5:  # Show first 5 rows
                print(f"   Row {row_idx}: {cell_texts[:10]}")  # First 10 cells
            
            # Look for subject codes (usually alphanumeric like ITITC601, CSE301, etc.)
            # Or look for "Days" column which often precedes subject codes
            has_subject_codes = any(
                bool(re.match(r'^[A-Z]{2,4}[A-Z]?\d{3,4}$', text)) 
                for text in cell_texts
            )
            
            if has_subject_codes or 'Days' in cell_texts:
                header_row = cell_texts
                header_row_idx = row_idx
                if debug:
                    print(f"\n   ✅ Found header row at index {row_idx}")
                    print(f"   Header: {header_row}")
                break
        
        if not header_row:
            if debug:
                print("   ⚠️  No header row found in this table")
            continue
        
        # Extract subject codes (skip first column which is usually "Days" or similar)
        subject_codes = []
        for i, cell in enumerate(header_row):
            if i == 0:  # Skip first column
                continue
            # Match subject code pattern
            if re.match(r'^[A-Z]{2,4}[A-Z]?\d{3,4}$', cell):
                subject_codes.append(cell)
            elif cell and cell != 'Days':  # Sometimes codes might be in different format
                subject_codes.append(cell)
        
        if debug:
            print(f"\n   📋 Extracted subject codes: {subject_codes}")
        
        # Now extract data rows
        data_rows = {}  # Store different metrics
        
        for row_idx, row in enumerate(rows[header_row_idx + 1:], start=header_row_idx + 1):
            cells = row.find_all(['td', 'th'])
            if len(cells) <= 1:
                continue
            
            first_cell = cells[0].get_text(strip=True)
            values = [cell.get_text(strip=True) for cell in cells[1:]]
            
            # Identify what this row contains
            row_type = None
            
            if any(keyword in first_cell for keyword in ['Overall (%)', 'Overall%', 'Attendance %', 'Percentage']):
                row_type = 'percentage'
            elif any(keyword in first_cell for keyword in ['Overall Class', 'Total Classes', 'Total Class']):
                row_type = 'total'
            elif 'Present' in first_cell and 'Overall' in first_cell:
                row_type = 'present'
            elif 'Absent' in first_cell and 'Overall' in first_cell:
                row_type = 'absent'
            
            if row_type:
                data_rows[row_type] = values
                if debug:
                    print(f"   {row_type.upper()}: {values[:5]}...")  # Show first 5
        
        if debug:
            print(f"\n   📊 Found data types: {list(data_rows.keys())}")
        
        # Build attendance records
        for i, subject_code in enumerate(subject_codes):
            record = {'Subject Code': subject_code}
            
            if 'percentage' in data_rows and i < len(data_rows['percentage']):
                record['Attendance %'] = data_rows['percentage'][i]
            
            if 'total' in data_rows and i < len(data_rows['total']):
                record['Total Classes'] = data_rows['total'][i]
            
            if 'present' in data_rows and i < len(data_rows['present']):
                record['Classes Present'] = data_rows['present'][i]
            
            if 'absent' in data_rows and i < len(data_rows['absent']):
                record['Classes Absent'] = data_rows['absent'][i]
            
            attendance_data.append(record)
        
        if debug and attendance_data:
            print(f"\n   ✅ Extracted {len(attendance_data)} subject records from this table")
    
    # Extract subject names from HTML
    # Look for patterns like "ITITC601-Web Technology" or "CSE301 - Data Structures"
    full_html = str(soup)
    
    for code in set(item['Subject Code'] for item in attendance_data):
        # Pattern 1: CODE-Name
        pattern1 = rf'{code}\s*-\s*([^<\n]+?)(?:<br>|<|$)'
        match = re.search(pattern1, full_html, re.IGNORECASE)
        
        if match:
            name = match.group(1).strip()
            # Clean up
            name = re.sub(r'---?>.*$', '', name).strip()
            name = re.sub(r'\s+', ' ', name).strip()
            subject_names[code] = name
        else:
            # Pattern 2: Look in nearby text
            # This is more aggressive - find the code and look at surrounding text
            pattern2 = rf'{code}[^A-Z0-9]{{0,3}}([A-Z][a-zA-Z\s&]+?)(?:<|$|[0-9])'
            match = re.search(pattern2, full_html)
            if match:
                name = match.group(1).strip()[:50]  # Limit to 50 chars
                subject_names[code] = name
    
    if debug:
        print(f"\n📚 Subject names found: {subject_names}")
    
    # Add subject names to records
    for item in attendance_data:
        code = item['Subject Code']
        if code in subject_names:
            item['Subject Name'] = subject_names[code]
        else:
            item['Subject Name'] = 'N/A'
    
    if debug:
        print("\n" + "="*80)
        print(f"✅ FINAL: Extracted {len(attendance_data)} total records")
        print("="*80)
    
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
        time.sleep(3)
    else:
        print("❌ Couldn't find 'My Activities' automatically")
        print("Please click it manually, then press Enter...")
        input()
    
    # Step 4: EXPAND the "Attendance" tree node
    print("\n🔍 Looking for 'Attendance' tree node to expand...")
    
    if find_and_expand_tree_node(driver, ['Attendance', 'ATTENDANCE']):
        print("🎉 Expanded 'Attendance' tree node!")
        time.sleep(3)
    else:
        print("⚠️  Could not find expandable 'Attendance' node automatically")
        print("Please click the '+' icon next to 'Attendance' manually, then press Enter...")
        input()
    
    # Step 5: Click "My Attendance"
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
            
            selects = driver.find_elements(By.TAG_NAME, "select")
            
            for select_elem in selects:
                select = Select(select_elem)
                
                select_name = select_elem.get_attribute("name") or select_elem.get_attribute("id") or ""
                
                if not year_selected and any(keyword in select_name.lower() for keyword in ['year', 'yr']):
                    print(f"\n📋 Found Year dropdown in {frame_name}:")
                    for i, opt in enumerate(select.options):
                        print(f"  [{i}] {opt.text}")
                    
                    year_choice = input("Enter the NUMBER in brackets: ")
                    select.select_by_index(int(year_choice))
                    print(f"✅ Selected: {select.options[int(year_choice)].text}")
                    year_selected = True
                    time.sleep(1)
                
                elif not semester_selected and any(keyword in select_name.lower() for keyword in ['sem', 'semester']):
                    print(f"\n📋 Found Semester dropdown in {frame_name}:")
                    for i, opt in enumerate(select.options):
                        print(f"  [{i}] {opt.text}")
                    
                    sem_choice = input("Enter the NUMBER in brackets: ")
                    select.select_by_index(int(sem_choice))
                    print(f"✅ Selected: {select.options[int(sem_choice)].text}")
                    semester_selected = True
                    time.sleep(1)
            
            if year_selected and semester_selected:
                print(f"\n🔍 Looking for Submit button in {frame_name}...")
                
                buttons = driver.find_elements(By.TAG_NAME, "input") + driver.find_elements(By.TAG_NAME, "button")
                
                for button in buttons:
                    button_type = button.get_attribute("type") or ""
                    button_value = (button.get_attribute("value") or button.text or "").lower()
                    button_name = (button.get_attribute("name") or "").lower()
                    
                    if 'pdf' in button_value or 'download' in button_value or 'mpdfx' in button_name:
                        continue
                    
                    if (button_type.lower() == "submit" and button_name == "submit") or button_value == "submit":
                        print(f"✅ Found Submit button!")
                        button.click()
                        print("🎉 Clicked Submit!")
                        time.sleep(5)
                        break
                
                break
                
        except Exception as e:
            continue
    
    if not year_selected or not semester_selected:
        print("\n⚠️  Couldn't find dropdowns automatically")
        print("Please select Year, Semester and click Submit manually")
        input("Press Enter once you've submitted...")
    
    # Step 7: Extract attendance data with enhanced parser
    print("\n📊 Extracting attendance data...")
    
    all_attendance = []
    
    for frame_name in ['data', 'contents', 'bottom', 'top']:
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(frame_name)
            
            html = driver.page_source
            
            # Check if this frame has attendance data
            if 'attend' in html.lower() and len(html) > 500:
                print(f"\n{'='*80}")
                print(f"✅ Found attendance data in '{frame_name}' frame!")
                print(f"{'='*80}")
                
                # Save raw HTML
                filename = f"attendance_{frame_name}.html"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"💾 Saved: {filename}")
                
                # Screenshot
                screenshot_name = f"attendance_{frame_name}.png"
                driver.save_screenshot(screenshot_name)
                print(f"📸 Saved: {screenshot_name}")
                
                # Parse with enhanced parser (debug mode ON)
                attendance_rows = extract_attendance_table_enhanced(html, debug=True)
                
                if attendance_rows:
                    print(f"\n✅ Successfully extracted {len(attendance_rows)} subject records!")
                    all_attendance.extend(attendance_rows)
                    
                    # Preview first 3
                    print(f"\n📋 Preview (first 3 subjects):")
                    for row in attendance_rows[:3]:
                        print(f"   {row}")
                else:
                    print("\n⚠️  Parser returned no data from this frame")
                
        except Exception as e:
            print(f"❌ Error in frame '{frame_name}': {e}")
            continue
    
    # Step 8: Save and display results
    if all_attendance:
        df = pd.DataFrame(all_attendance)
        
        # Reorder columns
        cols = ['Subject Code', 'Subject Name', 'Classes Present', 'Classes Absent', 'Total Classes', 'Attendance %']
        df = df[[col for col in cols if col in df.columns]]
        
        # Save to CSV
        csv_filename = "attendance_data.csv"
        df.to_csv(csv_filename, index=False)
        print(f"\n💾 Saved structured data to {csv_filename}")
        
        # Display summary
        print("\n" + "="*80)
        print("📊 YOUR ATTENDANCE SUMMARY")
        print("="*80)
        
        for _, row in df.iterrows():
            code = row.get('Subject Code', 'N/A')
            name = row.get('Subject Name', 'N/A')
            present = row.get('Classes Present', 'N/A')
            total = row.get('Total Classes', 'N/A')
            percentage = row.get('Attendance %', 'N/A')
            
            print(f"\n🎓 {code} - {name}")
            print(f"   Present: {present}/{total} classes")
            print(f"   Attendance: {percentage}%")
        
        print("\n" + "="*80)
        
        # Save Excel for better formatting
        try:
            excel_filename = "attendance_data.xlsx"
            df.to_excel(excel_filename, index=False, engine='openpyxl')
            print(f"💾 Also saved to {excel_filename}")
        except:
            print("⚠️  openpyxl not installed, skipping Excel export")
    else:
        print("\n⚠️  No attendance data was extracted!")
        print("Please check the HTML files manually to see the table structure")
    
    print("\n" + "="*60)
    print("✅ Scraping complete!")
    print("="*60)
    print("\n📁 Files created:")
    print("  - attendance_*.html (raw HTML)")
    print("  - attendance_*.png (screenshots)")
    if all_attendance:
        print("  - attendance_data.csv (structured data)")
        print("  - attendance_data.xlsx (Excel format)")
    
    print("\n🔍 Browser staying open for manual inspection")
    print("Press Enter to close...")
    input()

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    driver.save_screenshot("error.png")
    print("📸 Error screenshot saved as error.png")

finally:
    driver.quit()