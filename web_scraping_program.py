from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import csv

options = Options()
options.add_argument("--headless")
options.add_argument("user-agent=Mozilla/5.0")

try:
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    # Open the American League history page
    driver.get("https://www.baseball-almanac.com/yearmenu.shtml")
    time.sleep(5)

    # Find the year links for American League
    year_links = driver.find_elements(By.XPATH, '//td[contains(text(), "The History of the American League")]/ancestor::tr/following-sibling::tr[1]//a')

    if not year_links:
        print("No year links found on the page.")
    else:
        # Base URL to construct full links
        base_url = "https://www.baseball-almanac.com/yearly/"

        # Extract year and full URL
        year_urls = []
        for link in year_links:
            try:
                year_text = link.text.strip()
                href = link.get_attribute('href')
                if href:
                    full_url = base_url + href.split('/')[-1]
                    year_urls.append((year_text, full_url))
            except Exception as e:
                print(f"An error occurred processing a link: {e}")

        # Save to CSV
        with open('american_league_links.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Year", "URL"])
            writer.writerows(year_urls)

        print(f"Saved {len(year_urls)} links to 'american_league_links.csv'.")

except Exception as e:
    print(f"Exception: {type(e).__name__} {e}")

finally:
    driver.quit()