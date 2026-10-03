import sqlite3
from datetime import datetime
from dateutil.relativedelta import relativedelta
from compare import table_exists
mouthN = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",
          5:"May",6:"Jun",7:"Jul",8:"Aug",9:
          "Sep",10:"Oct",11:"Nov",12:"Dec"}

def room_count(tmouth:int,year:str):
    tmouth= mouthN[tmouth]
    target_month = f"{tmouth}_{year}"
    
    create_room_table(target_month)

    conn = sqlite3.connect('database_pkpd.db')
    c = conn.cursor()
    query = f"SELECT RES_ROOM, SUM(Total_Time) FROM {target_month} GROUP BY RES_ROOM"
    c.execute(query)
    results = c.fetchall()
    for row in results:
        room =row[0]
        TOTime = round(row[1], 2)

        insert_query = f"INSERT INTO {target_month}_ROOM (ROOM, TOTAL_TIME) VALUES (?, ?)"
        c.execute(insert_query, (room, TOTime))
        conn.commit()
    c.close()
    
def create_room_table(target_month):
    
        # Connect to the database
    conn = sqlite3.connect('database_pkpd.db')
    c = conn.cursor()
    if table_exists('database_pkpd.db', target_month) == False:        
            # SQL to create the room_report table
            # room_id is set as TEXT to match your existing Info table schema 
            # total_time is set as REAL to handle decimal hours/minutes 
        query = f"CREATE TABLE IF NOT EXISTS {target_month}_ROOM (ROOM TEXT, TOTAL_TIME REAL)"
            
        c.execute(query)
            
            # Changes are committed automatically by the 'with' block context manager
        
            
    else:
        query = f"DROP TABLE IF EXISTS {target_month}_ROOM"
        c.execute(query)
        query = f"CREATE TABLE IF NOT EXISTS {target_month}_ROOM (ROOM TEXT, TOTAL_TIME REAL)"
        c.execute(query)
        
    conn.commit()
    conn.close()


if __name__ == "__main__": 
    last_month_date = datetime.now() - relativedelta(months=1)
    Lmouth_Y =str(last_month_date.year)
    Lmouth =int(last_month_date.month)
    Uinput = input("Would you like to check the room report of last month? (Y/N)")
    if Uinput =="Y":
        room_count(Lmouth,Lmouth_Y)
    else:
        Uinput = input("Would you like to check the room report of other month? (Y/N)")
        if Uinput =="Y":
            Lmouth_Y =str(input("Enter the year you want to check"))
            Lmouth =int(input("Enter the month you want to check in integer"))
            room_count(Lmouth,Lmouth_Y)
        else:
            print("Program end")