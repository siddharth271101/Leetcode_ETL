import json
import pickle
import time
import pandas as pd
import bs4
import colorama
import requests
from colorama import Back, Fore
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from utils import *

# Initialize Colorama
colorama.init(autoreset=True)

# Setup Selenium Webdriver
CHROMEDRIVER_PATH = r"./driver/chromedriver"
options = Options()
options.headless = True
# Disable Warning, Error and Info logs
# Show only fatal errors
options.add_argument("--log-level=3")
driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)

    
if __name__ == "__main__":
    ALGORITHMS_ENDPOINT_URL = "https://leetcode.com/api/problems/algorithms/"

    # Problem URL is of format ALGORITHMS_BASE_URL + question__title_slug
    # If question__title_slug = "two-sum" then URL is https://leetcode.com/problems/two-sum
    ALGORITHMS_BASE_URL = "https://leetcode.com/problems/"

    # Load JSON from API
    algorithms_problems_json = requests.get(ALGORITHMS_ENDPOINT_URL).content
    algorithms_problems_json = json.loads(algorithms_problems_json)

    styles_str = "<style>pre{white-space:pre-wrap;background:#f7f9fa;padding:10px 15px;color:#263238;line-height:1.6;font-size:13px;border-radius:3px margin-top: 0;margin-bottom:1em;overflow:auto}b,strong{font-weight:bolder}#title{font-size:16px;color:#212121;font-weight:600;margin-bottom:10px}hr{height:10px;border:0;box-shadow:0 10px 10px -10px #8c8b8b inset}</style>"
    with open("out.html", "ab") as f:
            f.write(styles_str.encode(encoding="utf-8"))

    # List to store question_title_slug
    links = []
    question__title_slug = []
    question__article__slug = []
    question__title = []
    frontend_question_id = []
    difficulty = []
    for child in algorithms_problems_json["stat_status_pairs"]:
            # Only process free problems
            if not child["paid_only"]:
                question__title.append(child["stat"]["question__title"])
                frontend_question_id.append(child["stat"]["frontend_question_id"])
                difficulty.append(child["difficulty"]["level"])
                links.append(ALGORITHMS_BASE_URL+child["stat"]["question__title_slug"])

    dict = {
        "id":frontend_question_id,
        "Title":question__title,
        "URL":links,
        "difficulty":difficulty 
    }
    df = pd.DataFrame(dict)
    driver.quit()
    # print(df)