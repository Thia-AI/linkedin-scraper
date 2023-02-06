import argparse
import json
from dataclasses import dataclass

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import Options

from actions import login
from config import LINKEDIN_EMAIL, LINKEDIN_PASS
from helper import sleep_for_a_random_time
from person import Person

parser = argparse.ArgumentParser(prog='Linkedin Scraper', description='Scrapes linkedin profiles from a search term')


@dataclass
class Args:
    """Class that contains the data from parsing args"""
    search_term: str
    page_start: int
    page_end: int
    output_dir: str
    title: str


def url_encode_term(string):
    if not string:
        return ''
    key = string.split()
    keyword = ''
    for key1 in key:
        keyword = keyword + str(key1).capitalize() + "%20"
    return keyword.rstrip("%20")


def main(p_args: Args) -> None:
    print('Using email:', LINKEDIN_EMAIL)
    print('Using password:', LINKEDIN_PASS)
    search_term, page_start, page_end, output_dir = p_args.search_term, p_args.page_start, p_args.page_end, p_args.output_dir
    chrome_options = Options()
    # chrome_options.add_experimental_option('detach', True)
    driver = uc.Chrome(options=chrome_options,
                       user_data_dir='/Users/rahlawat/Library/Application Support/Google/Chrome/Profile 1')
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.maximize_window()
    login(driver, LINKEDIN_EMAIL, LINKEDIN_PASS, timeout=3)
    # Search
    search_keyword = url_encode_term(search_term)
    title_keyword = url_encode_term(p_args.title)
    out = []
    for page_no in range(page_start, page_end + 1):
        start = f"&page={page_no}"
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={search_keyword}&origin=SUGGESTION{start}&spellCorrectionEnabled=false&titleFreeText={title_keyword}"
        print(f'On page {page_no}: {search_url}')
        driver.get(search_url)
        search = BeautifulSoup(driver.page_source, 'lxml')
        potential_people = search.find_all('a', attrs={'data-test-app-aware-link': ''})
        # # Filter people by only LinkedIn URLs and filter out mutual connection links (that contain
        # "linkedin.com/in/ACoAA" in the href)
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
    file_name = f'{output_dir}/page_{page_start}_to_{page_end}.json' if page_start != page_end else f'{output_dir}/page_{page_start}.json'
    with open(file_name, 'w') as fp:
        json.dump(out, fp, indent=4)


if __name__ == '__main__':
    parser.add_argument('search_term', type=str, help='The term that will be searched in the linkedin search bar')
    parser.add_argument('-t', '--title', type=str, help='The job title of the people you are searching for')
    parser.add_argument('-ps', '--page_start', type=int,
                        default=1,
                        help='The page number of the search term for which to start the scraping at (default - 1, '
                             'must be >= 1)')
    parser.add_argument('-pe', '--page_end', type=int,
                        default=5,
                        help='The page number of the search term for which to end the scraping at (inclusive, '
                             'default - 5)')
    parser.add_argument('-od', '--output_dir', type=str, default='output',
                        help='Directory to output the scraped JSON file (default - ./output). JSON file will be '
                             'stored at output_dir/page_{page_start}_to_page_{page_end}.json')

    args = parser.parse_args()
    parsed_args = Args(search_term=args.search_term, title=args.title, page_start=args.page_start, page_end=args.page_end,
                       output_dir=args.output_dir)
    main(parsed_args)
