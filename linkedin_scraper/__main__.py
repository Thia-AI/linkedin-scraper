from bs4 import BeautifulSoup
from selenium import webdriver
from typing import Optional
from selenium.webdriver.chrome.webdriver import Options
from person import Person

from actions import login
from config import LINKEDIN_EMAIL, LINKEDIN_PASS


def main() -> None:
    print('Using email:', LINKEDIN_EMAIL)
    print('Using password:', LINKEDIN_PASS)
    chrome_options = Options()
    # chrome_options.add_experimental_option('detach', True)

    driver = webdriver.Chrome(options=chrome_options)
    login(driver, LINKEDIN_EMAIL, LINKEDIN_PASS)

    # Search
    # &spellCorrectionEnabled=false
    search_key = "AutoML"
    key = search_key.split()
    keyword = ''
    for key1 in key:
        keyword = keyword + str(key1).capitalize() + "%20"
    keyword = keyword.rstrip("%20")
    for page_no in range(1, 2):
        # start = f"&page={page_no}"
        # search_url = f"https://www.linkedin.com/search/results/people/?keywords={keyword}&origin=SUGGESTION{start}&spellCorrectionEnabled=false"
        # driver.get(search_url)
        # search = BeautifulSoup(driver.page_source, 'lxml')
        # potential_people = search.find_all('a', attrs={'data-test-app-aware-link': ''})
        # people = list(filter(lambda potential_person: potential_person.attrs['href'].startswith('https://www.linkedin.com/in/'), potential_people))
        # hrefs = [person.attrs['href'] for person in people]
        # hrefs = list(set(hrefs))
        # https://www.linkedin.com/in/shaghayegh-ds/details/interests/
        p = Person('https://www.linkedin.com/in/aditya-hicounselor/', driver=driver)
        print('````````````````````````````````')
        print('Name:')
        print(p.name)

        print('````````````````````````````````')
        print('Experiences:')
        print(p.experiences)

        print('````````````````````````````````')
        print('About:')
        print(p.about)

        print('````````````````````````````````')
        print('Accomplishments:')
        print(p.accomplishments)

        print('````````````````````````````````')
        print('Interests:')
        print(p.interests)





if __name__ == '__main__':
    main()
