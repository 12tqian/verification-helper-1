import onlinejudge_verify.online_submission.utils as utils

# import utils # for some reason this doesn't work...
import time
import requests
import os

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import colorlog

from logging import INFO, basicConfig, getLogger

logger = getLogger(__name__)

def push_debug() -> None:
    # read config
    logger.info('use GITHUB_TOKEN')  # NOTE: don't use GH_PAT here, because it may cause infinite loops with triggering GitHub Actions itself
    url = 'https://{}:{}@github.com/{}.git'.format(os.environ['GITHUB_ACTOR'], os.environ['GITHUB_TOKEN'], os.environ['GITHUB_REPOSITORY'])
    logger.info('GITHUB_ACTOR = %s', os.environ['GITHUB_ACTOR'])
    logger.info('GITHUB_REPOSITORY = %s', os.environ['GITHUB_REPOSITORY'])

    # commit and push
    subprocess.check_call(['git', 'config', '--global', 'user.name', 'GitHub'])
    subprocess.check_call(['git', 'config', '--global', 'user.email', 'noreply@github.com'])
    path = pathlib.Path('.verify-helper/dbg.png')
    logger.info('$ git add %s && git commit && git push', str(path))
    if path.exists():
        subprocess.check_call(['git', 'add', str(path)])
    if subprocess.run(['git', 'diff', '--quiet', '--staged'], check=False).returncode:
        message = '[auto-verifier] verify commit {}'.format(os.environ['GITHUB_SHA'])
        subprocess.check_call(['git', 'commit', '-m', message])
        subprocess.check_call(['git', 'push', url, 'HEAD'])


class VJudge:
    JUDGE_NAME = "vjudge"
    JUDGE_URL = "https://vjudge.net/"
    PROBLEM_URL = "https://vjudge.net/problem/"
    GOOD_VERDICTS = ["Accepted"]
    BAD_VERDICTS = [
        "Time",
        "Wrong",
        "Compilation",
        "Runtime",
        "Memory",
        "Output",
        "Presentation",
        "Compile",
        "Unknown",
    ]

    LANGUAGES = {
        "C": "43",  # GNU GCC C11 5.1.0
        "java": "36",  # Java 1.8.0_241
        "cpp": "61",  #
        "C++": "C++",  # C++ 17 64 bit
        "py": "41",  # PyPy 3.6 (7.2.0)
    }

    JUDGE_PREFIX = {
        "codeforces": "CodeForces",
        "atcoder": "AtCoder",
        "spoj": "SPOJ",
        "kattis": "Kattis",
    }

    JUDGE_MARKER = {
        "codeforces.com": "codeforces",
        "atcoder.jp": "atcoder",
        "spoj.com": "spoj",
        "open.kattis.com": "kattis",
    }

    JUDGE_LANGUAGE_VALUE = {
        "codeforces": {"C++": "61"},
        "atcoder": {"C++": "4003"},
        "kattis": {"C++": "C++"},
        "spoj": {"C++": "44"},
    }

    username: str
    password: str

    def check(self, verdict, verdict_list):
        for _verdict in verdict_list:
            if _verdict.lower() in verdict.lower():
                return True
        return False

    def current_millisecond_time(self):
        return round(time.time() * 1000)

    def __init__(self, username="", password=""):
        self.username = username
        self.password = password
        self.driver = None
        # configure logging
        log_format = "%(log_color)s%(levelname)s%(reset)s:%(name)s:%(message)s"
        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(log_format))
        basicConfig(level=INFO, handlers=[handler])

    def get_vjudge_problem_link(self, problem_link):
        judge_name = ""
        for marker in self.JUDGE_MARKER.keys():
            if marker in problem_link:
                judge_name = self.JUDGE_MARKER[marker]
                break
        if judge_name == "":
            return None
        add = ""
        lst = problem_link.split("/")
        if lst[-1] == "":
            lst.pop()
        if judge_name == "codeforces":
            if lst[-2] == "problem":
                add = lst[-3] + lst[-1]
            else:
                add = lst[-2] + lst[-1]
        elif judge_name == "atcoder" or judge_name == "spoj" or judge_name == "kattis":
            add = lst[-1]
        if judge_name == "atcoder":
            add = add.split("?")[0]  # get rid of language extension
        return [
            judge_name,
            self.PROBLEM_URL + self.JUDGE_PREFIX[judge_name] + "-" + add,
        ]

    def is_signed_in(self, driver):
        try:
            driver.find_element(By.CLASS_NAME, "logout")
            logger.info("Already signed in.")
            return True
        except NoSuchElementException:
            return False

    def sign_in(self, driver, url, username, password):
        logger.info("Signing in.")
        driver.get(url)
        utils.wait_for_page(driver, "Virtual Judge")

        try:
            action = ActionChains(driver)
            button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "login"))
            )
            action.move_to_element(button).click().perform()
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "btn-login"))
            )
        except NoSuchElementException:
            logger.error("Login button not present.")

        if not self.is_signed_in(driver):
            user = utils.wait_for_element(driver, "login-username")
            pwd = utils.wait_for_element(driver, "login-password")

            user.send_keys(username)
            pwd.send_keys(password)

            try:
                action = ActionChains(driver)
                button = utils.wait_for_element(driver, "btn-login")
                action.move_to_element(button).click().perform()
                WebDriverWait(driver, 5).until(EC.staleness_of(button))
            except NoSuchElementException:
                logger.error("Error signing in.")

    def submit_solution(self, problem_link, solution):
        if self.driver is None:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")  # Last I checked this was necessary.

            display = Display(visible=False, size=(800, 800)) # for some reason this is necessary
            display.start()
            # self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)

            self.driver = webdriver.Chrome(chrome_options=options)  # old version

        driver = self.driver
        print("signing in")
        self.sign_in(driver, self.JUDGE_URL, self.username, self.password)
        logger.info("Successfully signed in.")

        print("signed in")

        judge_name, submission_url = self.get_vjudge_problem_link(problem_link)

        MAX_RETRIES = 5
        retries = 1

        while retries <= MAX_RETRIES:
            logger.info(f"Trying ({retries}) times.")
            try:
                driver.get(submission_url)
                print("clicking submission button")
                # click submit button
                element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "/html/body/div[1]/div/div[1]/div[2]/div/div[1]/div[1]/button",
                        )
                    )
                )
                element.send_keys(Keys.ENTER)
                print("clicked submission button")
                # select language
                print("selecting language")
                element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "submit-language"))
                )
                value = self.JUDGE_LANGUAGE_VALUE[judge_name][solution.language]
                driver.execute_script(
                    """
                                        var select = arguments[0]; 
                                        for (var i = 0; i < select.options.length; i++) { 
                                            if (select.options[i].value == arguments[1]) { 
                                                select.options[i].selected = true; 
                                            } 
                                        }""",
                    element,
                    value,
                )
                print("selected language")
                print("inserting code")
                # insert code
                new_code = (
                    solution.solution_code
                    + "\n// "
                    + str(self.current_millisecond_time())
                )
                element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "submit-solution"))
                )
                element.send_keys(new_code)
                print("inserted code and waiting")
                time.sleep(3)  # 2 seconds for copy paste
                print("waiting finished and submitting")
                driver.save_screenshot('.verify-helper/dbg.png')
                push_debug()
                # click submit
                element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "/html/body/div[3]/div/div/div[3]/button[2]")
                    )
                )
                element.send_keys(Keys.RETURN)
                # element.click() 
                print("clicked submit")

                logger.info(f"Solution for {problem_link} submitted.")

                start = time.time()

                # repeat check for result
                while True:
                    try:
                        text = (
                            WebDriverWait(driver, 5)
                            .until(
                                EC.visibility_of_element_located(
                                    (
                                        By.XPATH,
                                        "/html/body/div[3]/div/div/div[2]/div[1]/table/tbody/tr[1]/td",
                                    )
                                )
                            )
                            .text
                        )
                    except:
                        text = ""
                    text = text.split(" ")[0]
                    if self.check(text, self.GOOD_VERDICTS):
                        driver.quit()
                        return True
                    elif self.check(text, self.BAD_VERDICTS):
                        driver.quit()
                        return False

                    time.sleep(0.25)
                    if time.time() - start >= 120:
                        break
            except:
                retries += 1
                driver.refresh()

        driver.quit()
        return False
