import json

from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.webdriver import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from actions import login
from config import LINKEDIN_EMAIL, LINKEDIN_PASS
from person import Person


def main() -> None:
    print('Using email:', LINKEDIN_EMAIL)
    print('Using password:', LINKEDIN_PASS)
    chrome_options = Options()
    chrome_options.add_argument("user-data-dir='/Users/rahlawat/Library/Application Support/Google/Chrome/Default'")
    # chrome_options.add_experimental_option('detach', True)
    driver = Chrome(options=chrome_options)

    login(driver, LINKEDIN_EMAIL, LINKEDIN_PASS, timeout=3)
    # Hide chat
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'msg-overlay-bubble-header__control')]")))
    hide_chat_button = driver.find_elements(By.XPATH,
                                            "//button[contains(@class, 'msg-overlay-bubble-header__control')]")
    hide_chat_button[-1].click()
    # Search
    # &spellCorrectionEnabled=false
    search_key = "AutoML"
    key = search_key.split()
    keyword = ''
    for key1 in key:
        keyword = keyword + str(key1).capitalize() + "%20"
    keyword = keyword.rstrip("%20")
    people = []
    for page_no in range(1, 2):
        # start = f"&page={page_no}"
        # search_url = f"https://www.linkedin.com/search/results/people/?keywords={keyword}&origin=SUGGESTION{start}&spellCorrectionEnabled=false"
        # driver.get(search_url)
        # search = BeautifulSoup(driver.page_source, 'lxml')
        # potential_people = search.find_all('a', attrs={'data-test-app-aware-link': ''})
        # # Filter people by only LinkedIn URLs and filter out mutual connection links (that contain "linkedin.com/in/ACoAA" in the href)
        # people = list(filter(lambda potential_person: potential_person.attrs['href'].startswith('https://www.linkedin.com/in/') and
        #                                               'linkedin.com/in/ACoAA' not in potential_person.attrs['href'],
        #                      potential_people))
        # hrefs = [person.attrs['href'] for person in people]
        # hrefs = list(set(hrefs))
        # for href in hrefs[:5]:
        #     href_query_params_removed = href.split('?')[0]
        # TODO: Fix bug of not getting experience of jobs where the person has had multiple roles
        p = Person('https://www.linkedin.com/in/mahtab-davoudi', driver=driver, close_on_complete=False)
        p_dict = p.as_dict()
        people.append(p_dict)
    with open('data.json', 'w') as fp:
        json.dump(people, fp, indent=4)


if __name__ == '__main__':
    main()
