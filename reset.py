import sqlite3 
from dateutil.relativedelta import relativedelta

import datetime
mouthN = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",
          5:"May",6:"Jun",7:"Jul",8:"Aug",9:
          "Sep",10:"Oct",11:"Nov",12:"Dec"}

def get_last_day_of_last_month():
    # 1. Get today's date
    today = datetime.date.today()
    
    # 2. Get the first day of the current month
    first_day_of_this_month = today.replace(day=1)
    
    # 3. Subtract one day to get the last day of the previous month
    last_day_of_last_month = first_day_of_this_month - datetime.timedelta(days=1)
    
    return last_day_of_last_month.day

def reset_count():
    last_month_date = datetime.datetime.now() - relativedelta(months=1)
    Lmouth_Y =int(last_month_date.year)
    Lmouth =int(last_month_date.month)
    mouthS = mouthN[Lmouth]
    last_day = get_last_day_of_last_month()
    last_month = (datetime.date.today().replace(day=1) - datetime.timedelta(days=1)).strftime("%m")
    this_month = datetime.datetime.now().strftime("%m")
    this_year = datetime.datetime.now().strftime("%Y")
    this_month_short = datetime.datetime.now().strftime("%b")

    LT = f"{Lmouth_Y}-{last_month}-{last_day} 23:59"
    ET = f"{this_year}-{this_month}-01 00:00"
    Lyear = str(Lmouth_Y)
    Tyear = str(this_year)

    conn = sqlite3.connect('database_pkpd.db')
    c = conn.cursor()
    query = "SELECT RES_NAME, ENTRY_COUNT, LEAVE_COUNT, RES_ID FROM Info WHERE living = 1"
    c.execute(query)
    records = c.fetchall()
    for row in records:
            res_name = row[0]
            entry_count = row[1]
            leave_count = row[2]
            res_id = row[3]
            
            if entry_count > leave_count:
                leave_count += 1  
                record_idl=f"{res_id}_{Lmouth_Y}_{mouthS}_{leave_count}"
                record_ide =f"{res_id}_{this_year}_{this_month_short}_1"
                c.execute("INSERT INTO REC_LEAVE (RES_ID, LEAVE_TIME, REC_Number, YEAR_L, MOUTH_L) VALUES (?,?, ?, ?, ?)",(res_id, LT,record_idl,Lyear, mouthS,))
                conn.commit()
                c.execute("INSERT INTO REC_ENTRY (RES_ID, ENTRY_TIME, REC_Number, YEAR_E, MOUTH_E) VALUES (?,?, ?, ?, ?)",(res_id, ET,record_ide,Tyear,this_month_short ,))
                conn.commit()
                c.execute("UPDATE Info SET ENTRY_COUNT = 1, LEAVE_COUNT = 0 WHERE RES_ID = ? AND living= 1",(res_id,))
                conn.commit()
            else:    
                c.execute("UPDATE Info SET ENTRY_COUNT = 0, LEAVE_COUNT = 0 WHERE RES_ID = ? AND living = 1", (res_id,))
                conn.commit()
    conn.close()
            
                 

                



if __name__ == "__main__":  
    reset_count()