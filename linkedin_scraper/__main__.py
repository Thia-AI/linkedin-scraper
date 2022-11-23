import json

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import Options

from actions import login
from config import LINKEDIN_EMAIL, LINKEDIN_PASS
from helper import sleep_for_a_random_time
from person import Person


def main() -> None:
    print('Using email:', LINKEDIN_EMAIL)
    print('Using password:', LINKEDIN_PASS)
    chrome_options = Options()
    # chrome_options.add_experimental_option('detach', True)
    driver = uc.Chrome(options=chrome_options,
                       user_data_dir='/Users/rahlawat/Library/Application Support/Google/Chrome/Profile 1')
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.maximize_window()
    login(driver, LINKEDIN_EMAIL, LINKEDIN_PASS, timeout=3)
    # Search
    search_key = "AutoML"
    key = search_key.split()
    keyword = ''
    for key1 in key:
        keyword = keyword + str(key1).capitalize() + "%20"
    keyword = keyword.rstrip("%20")
    out = []
    page_start = 12
    page_end = 19
    for page_no in range(page_start, page_end + 1):
        start = f"&page={page_no}"
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={keyword}&origin=SUGGESTION{start}&spellCorrectionEnabled=false"
        print(f'On page {page_no}: {search_url}')
        driver.get(search_url)
        search = BeautifulSoup(driver.page_source, 'lxml')
        potential_people = search.find_all('a', attrs={'data-test-app-aware-link': ''})
        # # Filter people by only LinkedIn URLs and filter out mutual connection links (that contain "linkedin.com/in/ACoAA" in the href)
        people = list(filter(
            lambda potential_person: potential_person.attrs['href'].startswith('https://www.linkedin.com/in/') and
                                     'linkedin.com/in/ACoAA' not in potential_person.attrs['href'],
            potential_people))
        hrefs = [person.attrs['href'] for person in people]
        hrefs = list(set(hrefs))
        for href in hrefs:
            href_query_params_removed = href.split('?')[0]
            p = Person(href_query_params_removed, driver=driver, close_on_complete=False)
            sleep_for_a_random_time()
            p_dict = p.as_dict()
            out.append(p_dict)
    file_name = f'page_{page_start}_to_{page_end}.json' if page_start != page_end else f'page_{page_start}.json'
    with open(file_name, 'w') as fp:
        json.dump(out, fp, indent=4)


if __name__ == '__main__':
    main()
