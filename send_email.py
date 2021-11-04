import psycopg2
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


MY_ADDRESS = "myaddress@gmail.com"         # Replace with yours
MY_PASSWORD = "mypassword"      # Replace with yours
RECIPIENT_ADDRESS = "recipientaddress@gmail.com"  # Replace with yours

HOST_ADDRESS = 'smtp.gmail.com'   # Replace with yours
HOST_PORT = 587                          # Replace with yours

def get_leetcode_probs(conn,cur,df):
    try:
        select_query = "SELECT * from leetcode order by Title asc fetch first 10 rows only"

        cur.execute(select_query)
        leetcode_prob_records = cur.fetchall()
        id_list = []
        title_list = []
        url_list = []
        difficulty_list = []
        for row in leetcode_prob_records:
            # print("Id = ", row[0], )
            # print("Title = ", row[1])
            # print("URL  = ", row[2])
            # print("Difficulty  = ", row[3])
            id_list.append(row[0])
            title_list.append(row[1])
            url_list.append(row[2])
            difficulty_list.append(row[3])
        dict = {
        "id":id_list,
        "Title":title_list,
        "URL":url_list,
        "difficulty":difficulty_list 
        }
        df = pd.DataFrame(dict)
        print("Records fetched from PostgreSQL table")
    except (Exception, psycopg2.Error) as error:
        print("Error fetching data from PostgreSQL table", error)


    finally:
        # closing database connection
        if conn:
            cur.close()
            conn.close()
            print("PostgreSQL connection is closed \n")
        return df

def getMessageBody(df):
    numProblems=len(df)
    msg_body="Coding Problems for the Week"+ "\n"
    for x in range(0, numProblems):
        msg_body=msg_body+ "\n"+ str(x+1) + ": " + df.Title[x]+"\n"+df.URL[x]+"\n"
    return msg_body

def sendMessage(df):
    # Connection with the server
    server = smtplib.SMTP(host=HOST_ADDRESS, port=HOST_PORT)
    server.starttls()
    server.login(MY_ADDRESS, MY_PASSWORD)

    # Creation of the MIMEMultipart Object
    message = MIMEMultipart()

    # Setup of MIMEMultipart Object Header
    message['From'] = MY_ADDRESS
    message['To'] = RECIPIENT_ADDRESS
    message['Subject'] = "Weekly Leetcode Problems"

    # Creation of a MIMEText Part
    messageBody=getMessageBody(df)
    textPart = MIMEText(messageBody, 'plain')

    # Part attachment
    message.attach(textPart)

    # Send Email and close connection
    server.send_message(message)
    server.quit()
def del_leetcode_probs(conn,cur):
    try:
        delete_query = "delete from leetcode where Id in(select Id from leetcode order by Title asc fetch first 10 rows only)"
        cur.execute(delete_query)
        conn.commit()
        print("Records deleted from PostgreSQL table")

    except (Exception, psycopg2.Error) as error:
        print("Error deleting data from PostgreSQL table", error)

    finally:
        # closing database connection
        if conn:
            cur.close()
            conn.close()
            print("PostgreSQL connection is closed \n")
if __name__ == "__main__":
    conn = psycopg2.connect("host=localhost dbname=dbname user=user password=password")
    cur = conn.cursor()
    df = pd.DataFrame()
    df = get_leetcode_probs(conn,cur,df)
    sendMessage(df)
    conn = psycopg2.connect("host=localhost dbname=dbname user=user password=password")
    cur = conn.cursor()
    del_leetcode_probs(conn,cur)

