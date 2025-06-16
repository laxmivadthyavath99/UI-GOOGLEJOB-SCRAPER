import time
import json
import traceback
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def extract_contact_info(text):
    phone_pattern = r"\+?\d{1,4}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{4,6}"
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}"
    phone_numbers = re.findall(phone_pattern, text)
    email_addresses = re.findall(email_pattern, text)
    valid_phones = [p for p in phone_numbers if len(re.sub(r'\D', '', p)) >= 10]
    valid_emails = [e for e in email_addresses if "@" in e]
    return ", ".join(valid_phones) or "N/A", ", ".join(valid_emails) or "N/A"

def scrape_google_job_details(url):
    start_time = time.time()
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    # options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    jobs = []
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "EimVGf"))
        )
        cards = driver.find_elements(By.CLASS_NAME, "EimVGf")
        print("Number of cards found:", len(cards))
        for idx, card in enumerate(cards):
            try:
                print(f"Scraping job card {idx+1}")
                driver.execute_script("arguments[0].scrollIntoView();", card)
                card.click()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "NgUYpe"))
                )
                time.sleep(1)
                soup = BeautifulSoup(driver.page_source, "lxml")
                title_elem = soup.find("h1", class_="LZAQDf cS4Vcb-pGL6qe-IRrXtf")
                title = title_elem.get_text(strip=True) if title_elem else "N/A"
                company_elem = soup.find("div", class_="waQ7qe cS4Vcb-pGL6qe-ysgGef")
                location_elem = soup.find("div", class_="waQ7qe cS4Vcb-pGL6qe-ysgGef")
                if company_elem:
                    comp_loc_text = company_elem.get_text(strip=True)
                    parts = [p.strip() for p in comp_loc_text.split('•')]
                    company = parts[0] if len(parts) > 0 else "N/A"
                    location = parts[1] if len(parts) > 1 else "N/A"
                else:
                    company, location = "N/A", "N/A"
                #company = company_elem.get_text(strip=True) if company_elem else "N/A"
                #location_elem = soup.find("div", class_="waQ7qe cS4Vcb-pGL6qe-ysgGef")
                #location = location_elem.get_text(strip=True) if location_elem else "N/A"
                posted_elem = soup.find("span", class_="Yf9oye")
                posted = posted_elem.get_text(strip=True) if posted_elem else "N/A"
                desc_div = soup.find("div", class_="NgUYpe")
                description = desc_div.get_text(strip=True) if desc_div else "N/A"
                phone, email = extract_contact_info(description)
                apply_links = {}
                links_section = soup.find_all("div", class_="gwBWYe")
                for section in links_section:
                    for a in section.find_all("a"):
                        href = a.get("href")
                        text = a.get_text(strip=True)
                        if text:
                            apply_links[text] = href
                job_details = {
                    "Job Title": title,
                    "Company Name": company,
                    "Location": location,
                    "Posted Date": posted,
                    "Job Description": description,
                    "Phone Number": phone,
                    "Email Address": email,
                    "Apply Links": json.dumps(apply_links),
                    "Job Link": url
                }
                jobs.append(job_details)
            except Exception as e:
                print(f"Error scraping job card {idx+1}: {e}")
                traceback.print_exc()
                continue
    except Exception as e:
        print("Error scraping job listings:", e)
        traceback.print_exc()
    finally:
        driver.quit()
        print(f"Scraping took {time.time() - start_time:.2f} seconds")
    return jobs