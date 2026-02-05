"""
attendance_scraper_api.py
Refactored scraper that can be called by Flask API
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import re
import traceback


def scrape_attendance(roll_no, password, year_idx, semester_idx, captcha_solver=None, headless=False):
    """
    Scrape attendance data from IMS NSIT portal
    
    Args:
        roll_no (str): Student roll number
        password (str): Student password
        year_idx (int): Year dropdown index (0-based)
        semester_idx (int): Semester dropdown index (0-based)
        captcha_solver (callable, optional): Function to solve CAPTCHA, receives driver as argument
        headless (bool): Run browser in headless mode
        
    Returns:
        dict: {
            'success': bool,
            'data': list of dicts with attendance data,
            'error': str (only if success=False)
        }
    """
    
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    if headless:
        options.add_argument("--headless")
    
    driver = None
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        wait = WebDriverWait(driver, 10)
        
        # Step 1: Login
        driver.get("https://www.imsnsit.org/imsnsit/")
        
        login_link = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Student Login")))
        login_link.click()
        time.sleep(5)
        
        # Fill login form
        driver.switch_to.frame(0)  # banner frame
        
        uid_input = wait.until(EC.presence_of_element_located((By.ID, "uid")))
        uid_input.send_keys(roll_no)
        
        pwd_input = driver.find_element(By.ID, "pwd")
        pwd_input.send_keys(password)
        
        # Handle CAPTCHA
        if captcha_solver:
            captcha_text = captcha_solver(driver)
        else:
            # For API, we'll need to pass CAPTCHA text
            return {
                'success': False,
                'error': 'CAPTCHA required but no solver provided'
            }
        
        captcha_input = driver.find_element(By.ID, "cap")
        captcha_input.send_keys(captcha_text)
        
        login_button = driver.find_element(By.ID, "login")
        login_button.click()
        
        time.sleep(8)
        driver.switch_to.default_content()
        
        # Step 2: Navigate to My Activities
        if not _find_and_click_link(driver, ['My Activities', 'Activities']):
            return {'success': False, 'error': 'Could not find My Activities link'}
        
        time.sleep(5)
        
        # Step 3: Expand Attendance menu
        if not _find_and_expand_tree_node(driver, ['Attendance']):
            return {'success': False, 'error': 'Could not find Attendance menu'}
        
        time.sleep(3)
        
        # Step 4: Click My Attendance
        if not _find_and_click_link(driver, ['My Attendance'], exact_match=True):
            return {'success': False, 'error': 'Could not find My Attendance option'}
        
        time.sleep(5)
        
        # Step 5: Select Year and Semester
        form_submitted = False
        
        for frame_name in ['data', 'contents', 'bottom', 'top']:
            try:
                driver.switch_to.default_content()
                driver.switch_to.frame(frame_name)
                
                selects = driver.find_elements(By.TAG_NAME, "select")
                
                year_select = None
                sem_select = None
                
                for select_elem in selects:
                    select_name = (select_elem.get_attribute("name") or select_elem.get_attribute("id") or "").lower()
                    
                    if 'year' in select_name or 'yr' in select_name:
                        year_select = Select(select_elem)
                    elif 'sem' in select_name:
                        sem_select = Select(select_elem)
                
                if year_select and sem_select:
                    # Select values
                    year_select.select_by_index(year_idx)
                    time.sleep(1)
                    sem_select.select_by_index(semester_idx)
                    time.sleep(1)
                    
                    # Find and click submit
                    buttons = driver.find_elements(By.TAG_NAME, "input") + driver.find_elements(By.TAG_NAME, "button")
                    
                    for button in buttons:
                        button_type = button.get_attribute("type") or ""
                        button_value = (button.get_attribute("value") or button.text or "").lower()
                        button_name = (button.get_attribute("name") or "").lower()
                        
                        if 'pdf' in button_value or 'download' in button_value:
                            continue
                        
                        if (button_type.lower() == "submit" and button_name == "submit") or button_value == "submit":
                            button.click()
                            time.sleep(5)
                            form_submitted = True
                            break
                    
                    if form_submitted:
                        break
                        
            except:
                continue
        
        if not form_submitted:
            return {'success': False, 'error': 'Could not submit attendance form'}
        
        # Step 6: Extract attendance data
        attendance_data = []
        
        for frame_name in ['data', 'contents', 'bottom', 'top']:
            try:
                driver.switch_to.default_content()
                driver.switch_to.frame(frame_name)
                
                html = driver.page_source
                
                if 'attend' in html.lower() and len(html) > 500:
                    # Parse attendance data
                    parsed_data = _extract_attendance_table(html)
                    
                    if parsed_data:
                        attendance_data.extend(parsed_data)
                        break
                        
            except:
                continue
        
        if not attendance_data:
            return {'success': False, 'error': 'No attendance data found'}
        
        return {
            'success': True,
            'data': attendance_data
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Scraper error: {str(e)}',
            'traceback': traceback.format_exc()
        }
        
    finally:
        if driver:
            driver.quit()


def _find_and_click_link(driver, keywords, frame_names=['data', 'top', 'contents', 'bottom', 'banner'], exact_match=False):
    """Helper to find and click a link across frames"""
    for frame_name in frame_names:
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(frame_name)
            
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                link_text = link.text.strip()
                
                if exact_match:
                    if link_text in keywords:
                        link.click()
                        return True
                else:
                    if any(keyword.lower() in link_text.lower() for keyword in keywords):
                        link.click()
                        return True
        except:
            continue
    return False


def _find_and_expand_tree_node(driver, text_keywords, frame_names=['data', 'top', 'contents', 'bottom', 'banner']):
    """Find and expand a tree node (for menu items)"""
    for frame_name in frame_names:
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(frame_name)
            
            hitareas = driver.find_elements(By.CLASS_NAME, "hitarea")
            
            for hitarea in hitareas:
                classes = hitarea.get_attribute("class") or ""
                
                if "expandable-hitarea" in classes:
                    try:
                        parent = hitarea.find_element(By.XPATH, "./..")
                        text = parent.text.strip()
                        
                        if any(keyword.lower() in text.lower() for keyword in text_keywords):
                            hitarea.click()
                            time.sleep(2)
                            driver.switch_to.default_content()
                            return True
                    except:
                        continue
                        
        except:
            continue
    
    return False


def _extract_attendance_table(html):
    """
    Extract attendance data from HTML
    Returns list of dicts with attendance info
    """
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table')
    
    attendance_data = []
    
    for table in tables:
        rows = table.find_all('tr')
        
        # Find header row with subject codes
        header_row = None
        header_row_idx = -1
        
        for row_idx, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            
            # Look for subject codes (pattern: ITITC601, CSE301, etc.)
            has_subject_codes = any(
                bool(re.match(r'^[A-Z]{2,4}[A-Z]?\d{3,4}$', text)) 
                for text in cell_texts
            )
            
            if has_subject_codes or 'Days' in cell_texts:
                header_row = cell_texts
                header_row_idx = row_idx
                break
        
        if not header_row:
            continue
        
        # Extract subject codes
        subject_codes = []
        for i, cell in enumerate(header_row):
            if i == 0:
                continue
            if re.match(r'^[A-Z]{2,4}[A-Z]?\d{3,4}$', cell):
                subject_codes.append(cell)
        
        if not subject_codes:
            continue
        
        # Find subject names (usually 2 rows after header)
        subject_names = {}
        for row_offset in [1, 2]:
            if header_row_idx + row_offset < len(rows):
                name_row = rows[header_row_idx + row_offset]
                name_cells = name_row.find_all(['td', 'th'])
                
                for i, code in enumerate(subject_codes):
                    if i + 1 < len(name_cells):
                        name = name_cells[i + 1].get_text(strip=True)
                        if name and not name.isdigit():
                            subject_names[code] = name
        
        # Find attendance data (Present/Absent rows)
        attendance_rows = {'P': {}, 'A': {}}
        
        for row in rows[header_row_idx:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue
            
            first_cell = cells[0].get_text(strip=True)
            
            if first_cell in ['P', 'Present']:
                for i, code in enumerate(subject_codes):
                    if i + 1 < len(cells):
                        val = cells[i + 1].get_text(strip=True)
                        attendance_rows['P'][code] = int(val) if val.isdigit() else 0
                        
            elif first_cell in ['A', 'Absent']:
                for i, code in enumerate(subject_codes):
                    if i + 1 < len(cells):
                        val = cells[i + 1].get_text(strip=True)
                        attendance_rows['A'][code] = int(val) if val.isdigit() else 0
        
        # Build final data
        for code in subject_codes:
            present = attendance_rows['P'].get(code, 0)
            absent = attendance_rows['A'].get(code, 0)
            total = present + absent
            percentage = round((present / total * 100), 2) if total > 0 else 0
            
            attendance_data.append({
                'subject_code': code,
                'subject_name': subject_names.get(code, 'Unknown'),
                'classes_present': present,
                'classes_absent': absent,
                'total_classes': total,
                'attendance_percentage': percentage
            })
    
    return attendance_data


# For testing
if __name__ == "__main__":
    # Test with manual CAPTCHA input
    def manual_captcha_solver(driver):
        return input("Enter CAPTCHA: ")
    
    result = scrape_attendance(
        roll_no="YOUR_ROLL_NO",
        password="YOUR_PASSWORD",
        year_idx=0,
        semester_idx=0,
        captcha_solver=manual_captcha_solver
    )
    
    print(result)