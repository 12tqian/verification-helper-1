class Problem: 
    judge_name: str
    problem_id: str

    def __init__(self, judge_name, problem_id):
        self.judge_name = judge_name
        self.problem_id = problem_id

    def __str__(self): 
        return self.judge_name + ' ' + self.problem_id
    
class Solution:
    solution_code: str
    problem: Problem
    language: str
    
    def __init__(self, language, solution_code):
        self.solution_code = solution_code
        self.language = language

