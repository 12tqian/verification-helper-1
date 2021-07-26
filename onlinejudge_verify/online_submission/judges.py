from onlinejudge_verify.online_submission.submissions import *
from requests import session
import requests
import mechanize
import time
import json
import traceback

class Codeforces:
    JUDGE_NAME = "codeforces"
    JUDGE_URL = "https://codeforces.com/"
    LOGIN_URL = "https://codeforces.com/enter"
    SUBMISSION_URL = "https://codeforces.com/problemset/submit"
    RESULT_URL = "https://codeforces.com/contest/"
    LANGUAGES = {
        "C" : "43", #GNU GCC C11 5.1.0
        "java" : "36", # Java 1.8.0_241
        "cpp" : "61", # 
        "C++" : "61", # C++ 17 64 bit
        "py" : "41" #PyPy 3.6 (7.2.0)
    }

    username: str
    password: str
    logged_in: bool
    br: mechanize.Browser

    def __init__(self, username = "", password = ""):
        self.username = username
        self.password = password
        self.logged_in = False
        self.br = mechanize.Browser()

        # Browser options
        self.br.set_handle_equiv(True)
        self.br.set_handle_gzip(True)
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        self.br.set_handle_robots(False)
        self.br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time = 1)

        self.br.addheaders = [('User-agent', 'Chrome')]
        
    def login(self):
        # print("Trying to log into CodeForces: " + self.username)
        # The site we will navigate into, handling it's session
        self.br.open(self.LOGIN_URL)

        # Select the second (index one) form (the first form is a search query box)
        # Logging in
        self.br.select_form(nr = 1)
        self.logged_in = True
        
        self.br.form['handleOrEmail'] = self.username
        self.br.form['password'] = self.password

        res = self.br.submit()

        if res.geturl() == self.JUDGE_URL:
            # print("Logged In Successfully")
            return True
        else:
            # print("CF: Sorry, wrong username/password. Please try again.")
            self.logged_in = False
            return False

    def get_contest_number(self, problem_id):
        res = ''
        for i in range(len(problem_id)):
            if problem_id[i].isdigit():
                res += problem_id[i]
            else:
                break
        return int(res)

    def current_millisecond_time(self):
        return round(time.time() * 1000)

    def submit_solution(self, problem, solution):
        if not self.logged_in:
            self.login()
        self.br.open(self.SUBMISSION_URL)
        self.br.select_form(nr = 1)
        
        self.br.form.find_control(name = "programTypeId").value = [self.LANGUAGES[solution.language]]
        self.br.form.find_control(name = "submittedProblemCode").value = str(problem.problem_id)
        self.br.form.find_control(name = "source").value = solution.solution_code + "\n// " + str(self.current_millisecond_time())
        res = self.br.submit()
        if "https://codeforces.com/problemset/status?my=on" != str(res.geturl()):
            return ""
            
        # then we should check if the verdict has been given
        # should check repeatedly delaying 5-10 secs and stop when a verdict is given
        time.sleep(0.25)
        response = requests.get("https://codeforces.com/api/user.status?handle=" + self.username + "&from=1&count=1")
        submission_id = ""
        if response.status_code == 200:
            try:
                data = json.loads(response.content.decode('utf-8'))
            except:
                return False
            submission_id = data['result'][0]['id']
        else:   
            # print("Could't get submission id. Please try this problem again later.")
            return False

        submission_url = self.RESULT_URL + str(self.get_contest_number(problem.problem_id)) + '/submission/' + str(submission_id)

        # wait for result

        start = time.time()
        time.sleep(0.25)
        
        # print(submission_url)
        
        while True:
            if (time.time() - start >= 60):
                break
            response = requests.get("https://codeforces.com/api/user.status?handle=" + self.username + "&from=1&count=1")
            data = json.loads(response.content.decode('utf-8'))
            
            data = data['result'][0]

            if 'verdict' not in data.keys():
                continue
            
            try:
                verdict = str(data['verdict'])
            except:
                traceback.print_exc()
                print(data)
                return False

            if verdict == "TESTING":
                time.sleep(0.25)
            else:
                if verdict == "OK":
                    return True
                else:
                    return False
                break
        return False

