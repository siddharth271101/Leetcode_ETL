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
import psycopg2


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


def check_if_valid_data(df: pd.DataFrame) -> bool:
    if df.empty:
        print("No Problems downloaded. Finishing execution")
        return False 
    # Primary Key Check
    if pd.Series(df['id']).is_unique:
        pass
    else:
        raise Exception("Primary Key check is violated")
    # Check for nulls
    if df.isnull().values.any():
        raise Exception("Null values found")
    return True

def create_database():
        '''Creates and connects to postgres database. Returns cursor and connection to DB'''
        # connect to default database
        try:
            conn = psycopg2.connect("host=localhost dbname=dbname user=user password=password")
        except psycopg2.Error as e:
            print("Error: Could not make connection to the Postgres database")
            print(e)
        try:
            cur = conn.cursor()
        except psycopg2.Error as e:
            print("Error: Could not get cursor to the Database")
            print(e)
        conn.set_session(autocommit=True)
        cur.execute("DROP DATABASE IF EXISTS leetcodedb")
        cur.execute("CREATE DATABASE leetcodedb WITH ENCODING 'utf8' TEMPLATE template0")

        # close connection to default database
        conn.close()    

        # connect to leetcodedb database
        try:
            conn = psycopg2.connect("host=localhost dbname=dbname user=user password=password")
        except psycopg2.Error as e:
            print("Error: Could not make connection to the Postgres database")
            print(e)
        try:
            cur = conn.cursor()
        except psycopg2.Error as e:
            print("Error: Could not get cursor to the Database")
            print(e)

        return cur, conn
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

    if check_if_valid_data(df):
        print("Data valid, proceed to Load stage")
    
    cur, conn = create_database()
    sql_query = """
    CREATE TABLE IF NOT EXISTS Leetcode(
        Id INT PRIMARY KEY,
        Title VARCHAR(200) NOT NULL UNIQUE,
        URL VARCHAR(200) NOT NULL,
        Difficulty INT NOT NULL
    )
    """
    cur.execute(sql_query)
    conn.commit()
    print("Opened database successfully")
    Leetcode_problems_insert = ("""INSERT INTO Leetcode(
                                Id,
                                Title,
                                URL,
                                Difficulty)
                                VALUES (%s,%s,%s,%s)
                                """)
    for i, row in df.iterrows():
        cur.execute(Leetcode_problems_insert, list(row))
    #     print(list(row))
    conn.commit()
    cur.close()
    conn.close()
