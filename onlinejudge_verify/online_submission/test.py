from judges import *
from submissions import *
import requests

import time


def current_milli_time():
    return round(time.time() * 1000)


judge = VJudge("vhelperoj", "verificationpassword")
# problem = Problem('codeforces', '4A')
problem_link = "https://codeforces.com/problemset/problem/4/A"
solution = Solution(
    "C++",
    """#include <bits/stdc++.h>

using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    if (n > 2 && n % 2 == 0) {
        cout << "YES" << '\\n';
    } else {
        cout << "NO" << '\\n';
    }
    return 0; 
}""",
)

print(judge.submit_solution(problem_link, solution))
