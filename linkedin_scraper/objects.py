from dataclasses import dataclass

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

import constants as c


@dataclass
class Experience:
    from_date: str = None
    to_date: str = None
    description: str = None
    position_title: str = None
    duration: str = None
    location: str = None


@dataclass
class Education:
    from_date: str = None
    to_date: str = None
    description: str = None
    degree: str = None


@dataclass
class Skill:
    name: str = None


@dataclass
class Project:
    title: str = None
    description: str = None


@dataclass
class Scraper:
    driver: Chrome = None

    def is_signed_in(self):
        try:
            self.driver.find_element(By.ID, c.VERIFY_LOGIN_ID)
            return True
        except:
            pass
        return False


