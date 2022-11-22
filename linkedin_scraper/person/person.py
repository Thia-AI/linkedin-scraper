import os
from dataclasses import asdict

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from linkedin_scraper import linkedin_selectors
from linkedin_scraper.objects import Experience, Education, Scraper, Skill, Project
from linkedin_scraper.helper import sleep_for_a_random_time

def filter_hidden_span_tag(span: str):
    return span.split('\n')[0]


class Person(Scraper):
    __TOP_CARD = "pv-top-card"
    __WAIT_FOR_ELEMENT_TIMEOUT = 5

    def __init__(
            self,
            linkedin_url=None,
            driver=None,
            get=True,
            scrape=True,
            close_on_complete=True,
    ):
        self.linkedin_url = linkedin_url
        self.name = ''
        self.about = ''
        self.experiences = []
        self.educations = []
        self.also_viewed_urls = []
        self.skills = []
        self.projects = []

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

    def add_about(self, about: str):
        self.about = about

    def add_experience(self, experience):
        self.experiences.append(experience)

    def add_education(self, education):
        self.educations.append(education)

    def add_skill(self, skill: Skill):
        self.skills.append(skill)

    def add_project(self, project: Project):
        self.projects.append(project)

    def get_details_list(self):
        try:
            _ = WebDriverWait(self.driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "pvs-list"))
            )
            details = self.driver.find_element(By.CLASS_NAME, "pvs-list")
            if 'Nothing to see for now' in details.text:
                details = None
        except:
            details = None
        return details

    def scrape(self, close_on_complete: bool):
        if self.is_signed_in():
            self.scrape_logged_in()
        else:
            self.scrape_logged_in()
        if close_on_complete:
            self.driver.quit()

    def scrape_logged_in(self):
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

        self.name = self.driver.find_element(By.CLASS_NAME, linkedin_selectors.NAME).text.strip()

        # get about
        try:
            WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.ID,
                        "about",
                    )
                )
            )
            about_div = driver.find_element(By.ID, 'about')
            about_parent = about_div.find_element(By.XPATH, './..')
            about = about_parent.find_element(By.XPATH, './div[3]//span').text
        except:
            about = None
        if about:
            self.add_about(about)

        # Go to experience details
        self.driver.get(self.linkedin_url + '/details/experience')
        sleep_for_a_random_time()
        exp = self.get_details_list()

        if exp:
            exp_children = exp.find_elements(By.XPATH, "./*")
            for position in exp_children:
                position = position.find_element(By.CLASS_NAME, 'pvs-entity')
                experience_div = position.find_element(By.XPATH, "./div[2]/div/div[1]")

                try:
                    position_title = experience_div.find_element(By.XPATH, './div[1]/span/span').text
                    company = filter_hidden_span_tag(
                        experience_div.find_elements(By.CLASS_NAME, 't-normal')[0].text)
                    times = filter_hidden_span_tag(experience_div.find_elements(By.CLASS_NAME, 't-normal')[1].text)
                    from_to = times.split('·')[0].strip()
                    duration = times.split('·')[1].strip()
                    from_date = from_to.split('-')[0].strip()
                    to_date = from_to.split('-')[1].strip()
                    # Description is potentially missing
                    description = None
                    try:
                        description_div = position.find_element(By.XPATH, './div[2]/div[2]')
                        description = description_div.find_element(By.XPATH, './/*/span').text
                    except Exception as e:
                        pass
                    # location is potentially missing
                    location = None
                    try:
                        location = filter_hidden_span_tag(
                            experience_div.find_elements(By.CLASS_NAME, 't-normal')[2].text)
                    except:
                        pass
                    experience = Experience(
                        position_title=position_title,
                        from_date=from_date,
                        to_date=to_date,
                        duration=duration,
                        location=location,
                        description=description,
                        company=company
                    )
                    experience.institution_name = company
                    self.add_experience(experience)
                except:
                    # Experience may have multiple roles at the same company
                    try:
                        experience_div = position.find_element(By.XPATH, './div[2]')
                        company_div = experience_div.find_element(By.XPATH, './div[1]//a')
                        company = filter_hidden_span_tag(company_div.find_element(By.XPATH, './div').text)
                        stay_at_company_details = company_div.find_element(By.XPATH, './span[1]').text
                        duration = filter_hidden_span_tag(stay_at_company_details.split('·')[-1].strip())

                        positions_list = experience_div.find_elements(By.XPATH,
                                                                      "./div[2]//li[contains(@class, 'pvs-list__paged-list-item')]")
                        latest_pos_div = positions_list[0].find_element(By.XPATH, './/a')
                        oldest_pos_div = positions_list[-1].find_element(By.XPATH, './/a')

                        position_title = filter_hidden_span_tag(latest_pos_div.find_element(By.XPATH, './div').text)

                        latest_pos_times = filter_hidden_span_tag(latest_pos_div.find_element(By.XPATH, "./span[contains(@class, 't-black--light')]").text)
                        latest_pos_from_to = latest_pos_times.split('·')[0].strip()
                        to_date = latest_pos_from_to.split('-')[-1].strip()

                        oldest_pos_times = filter_hidden_span_tag(oldest_pos_div.find_element(By.XPATH, "./span[contains(@class, 't-black--light')]").text)
                        oldest_pos_from_to = oldest_pos_times.split('·')[0].strip()
                        from_date = oldest_pos_from_to.split('-')[0].strip()

                        # Description is potentially missing
                        description = None
                        try:
                            description = positions_list[0].find_element(By.XPATH, './div/div/div[2]/div[2]//span').text
                        except:
                            pass
                        # Location is potentially missing
                        location = None
                        try:
                            location = filter_hidden_span_tag(company_div.find_element(By.XPATH, './span[2]').text)
                        except:
                            pass
                        experience = Experience(
                            position_title=position_title,
                            from_date=from_date,
                            to_date=to_date,
                            duration=duration,
                            location=location,
                            description=description,
                            company=company
                        )
                        experience.institution_name = company
                        self.add_experience(experience)
                    except:
                        company = None
                        position_title = None
                        description = None
                        from_date, to_date, duration, location = (None, None, None, None)
                        experience = Experience(
                            position_title=position_title,
                            from_date=from_date,
                            to_date=to_date,
                            duration=duration,
                            location=location,
                            description=description,
                            company=company
                        )
                        experience.institution_name = company
                        self.add_experience(experience)


        # Get education
        self.driver.get(self.linkedin_url + '/details/education/')
        sleep_for_a_random_time()

        edu = self.get_details_list()

        if edu:
            edu_children = edu.find_elements(By.XPATH, './*')
            for school in edu_children:
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

        # Get Skills
        self.driver.get(self.linkedin_url + '/details/skills/')
        sleep_for_a_random_time()

        ski = self.get_details_list()

        if ski:
            skill_children = ski.find_elements(By.XPATH, './*')
            for skill in skill_children:
                skill = skill.find_element(By.CLASS_NAME, 'pvs-entity')
                try:
                    skill_title = filter_hidden_span_tag(skill.find_element(By.XPATH, './/span').text)
                    skill = Skill(skill_title)
                    self.add_skill(skill)
                except Exception as e:
                    pass

        # Get projects
        self.driver.get(self.linkedin_url + '/details/projects')
        sleep_for_a_random_time()

        proj = self.get_details_list()

        if proj:
            proj_children = proj.find_elements(By.XPATH, './*')
            for project in proj_children:
                project = project.find_element(By.CLASS_NAME, 'pvs-entity')
                project_div = project.find_element(By.XPATH, './div[2]')
                try:
                    project_title = filter_hidden_span_tag(
                        project_div.find_element(By.XPATH, './div[1]/div[1]/div[1]').text)
                    project_description = project_div.find_element(By.XPATH, './div[2]//*/span').text
                    project_obj = Project(project_title, project_description)
                    self.add_project(project_obj)
                except Exception as e:
                    pass

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
        return "{name}\n\nAbout:\n{about}\n\nExperience:\n{exp}\n\nEducation:\n{edu}\n\nSkill:\n{skill}\n\nProject:\n{proj}".format(
            name=self.name,
            about=self.about,
            exp=self.experiences,
            edu=self.educations,
            skill=self.skills,
            proj=self.projects
        )

    def as_dict(self):
        return {
            'name': self.name,
            'about': self.about,
            'experiences': [asdict(experience) for experience in self.experiences],
            'educations': [asdict(education) for education in self.educations],
            'skill': [asdict(skill) for skill in self.skills],
            'projects': [asdict(project) for project in self.projects]
        }
