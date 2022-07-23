import onlinejudge_verify.online_submission.utils as utils

# import utils # for some reason this doesn't work...
import time
import requests
import os
import subprocess
import pathlib

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


def push_debug(path) -> None:
    # read config
    logger.info(
        "use GITHUB_TOKEN"
    )  # NOTE: don't use GH_PAT here, because it may cause infinite loops with triggering GitHub Actions itself
    url = "https://{}:{}@github.com/{}.git".format(
        os.environ["GITHUB_ACTOR"],
        os.environ["GITHUB_TOKEN"],
        os.environ["GITHUB_REPOSITORY"],
    )
    logger.info("GITHUB_ACTOR = %s", os.environ["GITHUB_ACTOR"])
    logger.info("GITHUB_REPOSITORY = %s", os.environ["GITHUB_REPOSITORY"])

    # commit and push
    logger.info("starting push")
    subprocess.check_call(["git", "config", "--global", "user.name", "GitHub"])
    subprocess.check_call(
        ["git", "config", "--global", "user.email", "noreply@github.com"]
    )
    logger.info("pushing")
    path = pathlib.Path(path)
    logger.info("$ git add %s && git commit && git push", str(path))
    if path.exists():
        subprocess.check_call(["git", "add", str(path)])
    if subprocess.run(["git", "diff", "--quiet", "--staged"], check=False).returncode:
        message = "[auto-verifier] verify commit {}".format(
            os.environ["GITHUB_SHA"])
        subprocess.check_call(["git", "commit", "-m", message])
        subprocess.check_call(["git", "push", url, "HEAD"])


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
            element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/nav/div/ul/li[9]/a"))
            )
            element.send_keys(Keys.RETURN)
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[4]/div/div/div[3]/button[3]")
                )
            )
        except NoSuchElementException:
            logger.error("Login button not present.")

        if not self.is_signed_in(driver):
            user = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     "/html/body/div[4]/div/div/div[2]/form/div[1]/input")
                )
            )

            pwd = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     "/html/body/div[4]/div/div/div[2]/form/div[2]/input")
                )
            )

            user.send_keys(username)
            pwd.send_keys(password)

            time.sleep(0.5)

            try:
                element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH,
                         "/html/body/div[4]/div/div/div[3]/button[3]")
                    )
                )
                element.send_keys(Keys.RETURN)
                time.sleep(0.5)
            except NoSuchElementException:
                logger.error("Error signing in.")

    def submit_solution(self, problem_link, solution):
        options = Options()
        options.add_argument("--headless")
        # Last I checked this was necessary.
        options.add_argument("--disable-gpu")

        display = Display(
            visible=False, size=(800, 800)
        )  # for some reason this is necessary
        display.start()
        # self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)

        self.driver = webdriver.Chrome(chrome_options=options)  # old version

        driver = self.driver

        self.sign_in(driver, self.JUDGE_URL, self.username, self.password)
        logger.info("Successfully signed in.")

        judge_name, submission_url = self.get_vjudge_problem_link(problem_link)

        MAX_RETRIES = 5
        retries = 1

        while retries <= MAX_RETRIES:
            logger.info(f"Trying ({retries}) times.")
            try:
                logger.info(f"Navigating to {submission_url} .")
                driver.get(submission_url)

                # click submit button
                logger.info(f"Clicking submit buttton for {problem_link} .")
                element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "/html/body/div[1]/div/div[1]/div[2]/div/div[1]/div[1]/button",
                        )
                    )
                )
                element.send_keys(Keys.RETURN)

                # select language
                logger.info(f"Selecting language for {problem_link} .")
                element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "/html/body/div[3]/div/div/div[2]/form/div/div[4]/div[2]/div/select",
                        )
                    )
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
                time.sleep(0.5)

                # insert code
                logger.info(f"Inputting code for {problem_link}.")
                new_code = (
                    solution.solution_code
                    + "\n// "
                    + str(self.current_millisecond_time())
                )
                element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "/html/body/div[3]/div/div/div[2]/form/div/div[4]/div[4]/div/textarea",
                        )
                    )
                )
                driver.execute_script(
                    "arguments[0].value = arguments[1];", element, new_code
                )
                time.sleep(2)  # 2 seconds for copy paste

                # click submit
                logger.info(f"Clicking final submission {problem_link} .")
                element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH,
                         "/html/body/div[3]/div/div/div[3]/button[2]")
                    )
                )
                element.send_keys(Keys.RETURN)

                logger.info(f"Solution for {problem_link} submitted.")

                start = time.time()

                # repeatedly check for result
                checked_times = 1
                inserted = 0
                while True:
                    if inserted == 0 and checked_times > 5:  # we must be actually verified
                        break
                    logger.info(
                        f"Checking submission {checked_times} times for {problem_link} ."
                    )
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
                        inserted += 1
                    except:
                        text = ""
                    text = text.split(" ")[0]
                    if self.check(text, self.GOOD_VERDICTS):
                        logger.info("{problem_link} was successful.")
                        driver.quit()
                        return True
                    elif self.check(text, self.BAD_VERDICTS):
                        logger.info("{problem_link} failed.")
                        driver.quit()
                        return False

                    time.sleep(3)
                    checked_times += 1
                    if time.time() - start >= 120:
                        break
            except:
                retries += 1
                driver.refresh()
        driver.quit()
        return False
