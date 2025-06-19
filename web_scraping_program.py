from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import time
import csv

options = Options()
options.add_argument("--headless")
options.add_argument("user-agent=Mozilla/5.0")

batting_stats = []      # [Year, Stat, Player, Team, Value]
pitching_stats = []     # [Year, Stat, Player, Team, Value]
defective_links = []    # [Year, URL (Issue)]

try:
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.get("https://www.baseball-almanac.com/yearmenu.shtml")
    time.sleep(5)

    year_links = driver.find_elements(By.XPATH, '//td[contains(text(), "The History of the American League")]/ancestor::tr/following-sibling::tr[1]//a')
    if not year_links:
        print("No year links found.")
        driver.quit()
        exit()

    base_url = "https://www.baseball-almanac.com/yearly/"
    year_urls = []
    for link in year_links:
        year_text = link.text.strip()
        href = link.get_attribute('href')
        if href:
            full_url = base_url + href.split('/')[-1]
            year_urls.append((year_text, full_url))

    print(f"Collected {len(year_urls)} year URLs")

    for year, url in year_urls:
        try:
            print(f"Processing year {year}")
            driver.get(url)
            time.sleep(3)

            # Hitting Statistics League Leaders - Base on Balls
            try:
                row = driver.find_element(By.XPATH, '//td/a[contains(text(), "Base on Balls")]/ancestor::tr')
                cols = row.find_elements(By.TAG_NAME, 'td')
                if len(cols) >= 4:
                    stat = "Base on Balls"
                    player = cols[1].text.strip()
                    team = cols[2].text.strip()
                    value = cols[3].text.strip()
                    batting_stats.append([year, stat, player, team, value])
            except NoSuchElementException:
                defective_links.append((year, url + " (missing Base on Balls)"))

            # Hitting Statistics League Leaders - Home Runs
            try:
                row = driver.find_element(By.XPATH, '//td/a[contains(text(), "Home Runs")]/ancestor::tr')
                cols = row.find_elements(By.TAG_NAME, 'td')
                if len(cols) >= 4:
                    stat = "Home Runs"
                    player = cols[1].text.strip()
                    team = cols[2].text.strip()
                    value = cols[3].text.strip()
                    batting_stats.append([year, stat, player, team, value])
            except NoSuchElementException:
                defective_links.append((year, url + " (missing Home Runs)"))

            # Pitching Statistics League Leaders - Wins
            try:
                row = driver.find_element(By.XPATH, '//td/a[contains(text(), "Wins")]/ancestor::tr')
                cols = row.find_elements(By.TAG_NAME, 'td')
                if len(cols) >= 4:
                    stat = "Wins"
                    player = cols[1].text.strip()
                    team = cols[2].text.strip()
                    value = cols[3].text.strip()
                    pitching_stats.append([year, stat, player, team, value])
            except NoSuchElementException:
                defective_links.append((year, url + " (missing Wins)"))

            # Pitching Statistics League Leaders - ERA 
            try:
                row = driver.find_element(By.XPATH, '//td/a[contains(text(), "ERA")]/ancestor::tr')
                cols = row.find_elements(By.TAG_NAME, 'td')
                if len(cols) >= 4:
                    stat = "ERA"
                    player = cols[1].text.strip()
                    team = cols[2].text.strip()
                    value = cols[3].text.strip()
                    pitching_stats.append([year, stat, player, team, value])
            except NoSuchElementException:
                defective_links.append((year, url + " (missing ERA)"))

        except (TimeoutException, WebDriverException) as e:
            defective_links.append((year, url + f" (load error: {type(e).__name__})"))

except Exception as e:
    print(f"Error: {e}")

finally:
    driver.quit()

# Save CSVs
def save_csv(filename, header, data):
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)

save_csv('batting_stats.csv', ["Year", "Stat", "Player", "Team", "Value"], batting_stats)
save_csv('pitching_stats.csv', ["Year", "Stat", "Player", "Team", "Value"], pitching_stats)
save_csv('defective_links.csv', ["Year", "URL (Issue)"], defective_links)

print(f"\nPlayer batting entries collected: {len(batting_stats)}")
print(f"Player pitching entries collected: {len(pitching_stats)}")
print(f"Defective or skipped entries: {len(defective_links)}")
