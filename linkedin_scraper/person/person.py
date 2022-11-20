import os

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from linkedin_scraper import selectors
from linkedin_scraper.objects import Experience, Education, Scraper, Interest, Accomplishment, Contact


class Person(Scraper):
    __TOP_CARD = "pv-top-card"
    __WAIT_FOR_ELEMENT_TIMEOUT = 5

    def __init__(
            self,
            linkedin_url=None,
            name=None,
            about=None,
            experiences=None,
            educations=None,
            interests=None,
            accomplishments=None,
            company=None,
            job_title=None,
            contacts=None,
            driver=None,
            get=True,
            scrape=True,
            close_on_complete=True,
    ):
        self.linkedin_url = linkedin_url
        self.name = name
        self.about = about or []
        self.experiences = experiences or []
        self.educations = educations or []
        self.interests = interests or []
        self.accomplishments = accomplishments or []
        self.also_viewed_urls = []
        self.contacts = contacts or []

        if driver is None:
            try:
                if os.getenv("CHROMEDRIVER") == None:
                    driver_path = os.path.join(
                        os.path.dirname(__file__), "drivers/chromedriver"
                    )
                else:
                    driver_path = os.getenv("CHROMEDRIVER")

                driver = webdriver.Chrome(driver_path)
            except:
                driver = webdriver.Chrome()

        if get:
            driver.get(linkedin_url)

        self.driver = driver

        self.actions = ActionChains(self.driver)

        if scrape:
            self.scrape(close_on_complete)

    def add_about(self, about):
        self.about.append(about)

    def add_experience(self, experience):
        self.experiences.append(experience)

    def add_education(self, education):
        self.educations.append(education)

    def add_interest(self, interest):
        self.interests.append(interest)

    def add_accomplishment(self, accomplishment):
        self.accomplishments.append(accomplishment)

    def add_location(self, location):
        self.location = location

    def add_contact(self, contact):
        self.contacts.append(contact)

    def scrape(self, close_on_complete=True):
        if self.is_signed_in():
            self.scrape_logged_in(close_on_complete=close_on_complete)
        else:
            print("you are not logged in!")
            x = input("please verify the capcha then press any key to continue...")
            self.scrape_not_logged_in(close_on_complete=close_on_complete)

    def filter_hidden_span_tag(self, span: str):
        return span.split('\n')[0]

    def _click_see_more_by_section(self, section_name):
        section_class_name = 'pvs-list__footer-wrapper'
        try:
            _ = WebDriverWait(self.driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, section_class_name))
            )
            divs = self.driver.find_elements(By.CLASS_NAME, section_class_name)
            for div in divs:
                button = div.find_element(By.TAG_NAME, "a")
                button_text = div.find_element(By.TAG_NAME, 'span').text
                if section_name in button_text:
                    self.actions.move_to_element(button).perform()
                    button.click()
                    return
        except Exception as e:
            pass

    def scrape_logged_in(self, close_on_complete=True):
        driver = self.driver
        duration = None

        root = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.presence_of_element_located(
                (
                    By.CLASS_NAME,
                    self.__TOP_CARD,
                )
            )
        )

        self.name = self.driver.find_element(By.CLASS_NAME, selectors.NAME).text.strip()

        # get about
        try:
            see_more = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[@class='lt-line-clamp__more']",
                    )
                )
            )
            driver.execute_script("arguments[0].click();", see_more)

            about = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[@class='lt-line-clamp__raw-line']",
                    )
                )
            )
        except:
            about = None
        if about:
            self.add_about(about.text.strip())

        # Go to experience details
        self.driver.get(self.linkedin_url + 'details/experience')

        try:
            _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "pvs-list"))
            )
            exp = driver.find_element(By.CLASS_NAME, "pvs-list")

        except:
            exp = None

        if exp:
            child_exp = exp.find_elements(By.XPATH, "./*")
            for position in child_exp:
                position = position.find_element(By.CLASS_NAME, 'pvs-entity')
                experience_div = position.find_element(By.XPATH, ".//div[2]/div/div[1]")
                position_title = experience_div.find_element(By.XPATH, './/div[1]/span/span').text

                try:
                    company = self.filter_hidden_span_tag(
                        experience_div.find_elements(By.CLASS_NAME, 't-normal')[0].text)
                    times = self.filter_hidden_span_tag(experience_div.find_elements(By.CLASS_NAME, 't-normal')[1].text)
                    location = self.filter_hidden_span_tag(
                        experience_div.find_elements(By.CLASS_NAME, 't-normal')[2].text)
                    from_to = times.split('·')[0].strip()
                    duration = times.split('·')[1].strip()
                    from_date = from_to.split('-')[0].strip()
                    to_date = from_to.split('-')[1].strip()
                except:
                    company = None
                    from_date, to_date, duration, location = (None, None, None, None)

                experience = Experience(
                    position_title=position_title,
                    from_date=from_date,
                    to_date=to_date,
                    duration=duration,
                    location=location,
                )
                experience.institution_name = company
                self.add_experience(experience)

        # Get education
        self.driver.get(self.linkedin_url + 'details/education')

        try:
            _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "pvs-list"))
            )
            edu = driver.find_element(By.CLASS_NAME, "pvs-list")

        except:
            edu = None

        if edu:
            child_edu = edu.find_elements(By.XPATH, './*')
            for school in child_edu:
                school = school.find_element(By.CLASS_NAME, 'pvs-entity')
                school_div = school.find_element(By.XPATH, './div[2]/div/a')
                university = school_div.find_element(By.XPATH, './div[1]/span/span').text

                try:
                    degree = school_div.find_element(By.XPATH, './span[1]/span[1]').text
                    times = school_div.find_element(By.XPATH, './span[2]/span[1]').text
                    from_date = times.split('-')[0].strip()
                    to_date = times.split('-')[1].strip()

                except:
                    degree = None
                    from_date, to_date = (None, None)
                education = Education(
                    from_date=from_date, to_date=to_date, degree=degree
                )
                education.institution_name = university
                self.add_education(education)

        # Get interests
        self.driver.get(self.linkedin_url)
        try:

            _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[@class='pv-profile-section pv-interests-section artdeco-container-card artdeco-card ember-view']",
                    )
                )
            )
            interestContainer = driver.find_element(By.XPATH,
                                                    "//*[@class='pv-profile-section pv-interests-section artdeco-container-card artdeco-card ember-view']"
                                                    )
            for interestElement in interestContainer.find_elements(By.XPATH,
                                                                   "//*[@class='pv-interest-entity pv-profile-section__card-item ember-view']"
                                                                   ):
                interest = Interest(
                    interestElement.find_element(By.TAG_NAME, "h3").text.strip()
                )
                self.add_interest(interest)
        except:
            pass

        # get accomplishment
        try:
            _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[@class='pv-profile-section pv-accomplishments-section artdeco-container-card artdeco-card ember-view']",
                    )
                )
            )
            acc = driver.find_element(By.XPATH,
                                      "//*[@class='pv-profile-section pv-accomplishments-section artdeco-container-card artdeco-card ember-view']"
                                      )
            for block in acc.find_elements(By.XPATH,
                                           "//div[@class='pv-accomplishments-block__content break-words']"
                                           ):
                category = block.find_element(By.TAG_NAME, "h3")
                for title in block.find_element(By.TAG_NAME,
                                                "ul"
                                                ).find_elements(By.TAG_NAME, "li"):
                    accomplishment = Accomplishment(category.text, title.text)
                    self.add_accomplishment(accomplishment)
        except:
            pass

        # get connections
        try:
            driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
            _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "mn-connections"))
            )
            connections = driver.find_element(By.TAG_NAME, "mn-connections")
            if connections is not None:
                for conn in connections.find_elements(By.CLASS_NAME, "mn-connection-card"):
                    anchor = conn.find_element(By.CLASS_NAME, "mn-connection-card__link")
                    url = anchor.get_attribute("href")
                    name = conn.find_element(By.CLASS_NAME, "mn-connection-card__details").find_element(By.CLASS_NAME,
                                                                                                        "mn-connection-card__name").text.strip()
                    occupation = conn.find_element(By.CLASS_NAME,
                                                   "mn-connection-card__details").find_element(By.CLASS_NAME,
                                                                                               "mn-connection-card__occupation").text.strip()

                    contact = Contact(name=name, occupation=occupation, url=url)
                    self.add_contact(contact)
        except:
            connections = None

        if close_on_complete:
            driver.quit()

    def scrape_not_logged_in(self, close_on_complete=True, retry_limit=10):
        driver = self.driver
        retry_times = 0
        while self.is_signed_in() and retry_times <= retry_limit:
            driver.get(self.linkedin_url)
            retry_times = retry_times + 1

        # get name
        self.name = driver.find_element(By.CLASS_NAME,
                                        "top-card-layout__title"
                                        ).text.strip()

        # get experience
        try:
            _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "experience"))
            )
            exp = driver.find_element(By.CLASS_NAME, "experience")
        except:
            exp = None

        if exp is not None:
            for position in exp.find_elements(By.CLASS_NAME,
                                              "experience-item__contents"
                                              ):
                position_title = position.find_element(By.CLASS_NAME,
                                                       "experience-item__title"
                                                       ).text.strip()
                company = position.find_element(By.CLASS_NAME,
                                                "experience-item__subtitle"
                                                ).text.strip()

                try:
                    times = position.find_element(By.CLASS_NAME,
                                                  "experience-item__duration"
                                                  )
                    from_date = times.find_element(By.CLASS_NAME,
                                                   "date-range__start-date"
                                                   ).text.strip()
                    try:
                        to_date = times.find_element(By.CLASS_NAME,
                                                     "date-range__end-date"
                                                     ).text.strip()
                    except:
                        to_date = "Present"
                    duration = position.find_element(By.CLASS_NAME,
                                                     "date-range__duration"
                                                     ).text.strip()
                    location = position.find_element(By.CLASS_NAME,
                                                     "experience-item__location"
                                                     ).text.strip()
                except:
                    from_date, to_date, duration, location = (None, None, None, None)

                experience = Experience(
                    position_title=position_title,
                    from_date=from_date,
                    to_date=to_date,
                    duration=duration,
                    location=location,
                )
                experience.institution_name = company
                self.add_experience(experience)
        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/1.5));"
        )

        # get education
        edu = driver.find_element(By.CLASS_NAME, "education__list")
        for school in edu.find_elements(By.CLASS_NAME, "result-card"):
            university = school.find_element(By.CLASS_NAME,
                                             "result-card__title"
                                             ).text.strip()
            degree = school.find_element(By.CLASS_NAME,
                                         "education__item--degree-info"
                                         ).text.strip()
            try:
                times = school.find_element(By.CLASS_NAME, "date-range")
                from_date = times.find_element(By.CLASS_NAME,
                                               "date-range__start-date"
                                               ).text.strip()
                to_date = times.find_element(By.CLASS_NAME,
                                             "date-range__end-date"
                                             ).text.strip()
            except:
                from_date, to_date = (None, None)
            education = Education(from_date=from_date, to_date=to_date, degree=degree)

            education.institution_name = university
            self.add_education(education)

        if close_on_complete:
            driver.close()

    @property
    def company(self):
        if self.experiences:
            return (
                self.experiences[0].institution_name
                if self.experiences[0].institution_name
                else None
            )
        else:
            return None

    @property
    def job_title(self):
        if self.experiences:
            return (
                self.experiences[0].position_title
                if self.experiences[0].position_title
                else None
            )
        else:
            return None

    def __repr__(self):
        return "{name}\n\nAbout\n{about}\n\nExperience\n{exp}\n\nEducation\n{edu}\n\nInterest\n{int}\n\nAccomplishments\n{acc}\n\nContacts\n{conn}".format(
            name=self.name,
            about=self.about,
            exp=self.experiences,
            edu=self.educations,
            int=self.interests,
            acc=self.accomplishments,
            conn=self.contacts,
        )
