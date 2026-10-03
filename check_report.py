import sqlite3
from datetime import datetime
from dateutil.relativedelta import relativedelta
from compare import table_exists
mouthN = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",
          5:"May",6:"Jun",7:"Jul",8:"Aug",9:
          "Sep",10:"Oct",11:"Nov",12:"Dec"}

def print_low_usage_rooms(target_month, target_year):
    tmouth= mouthN[target_month]
    target_month = f"{tmouth}_{target_year}"
    
    conn = sqlite3.connect('database_pkpd.db')
    c = conn.cursor()
        
    
    query = f"SELECT ROOM, TOTAL_TIME FROM {target_month}_ROOM WHERE Total_Time < 150"
        
    c.execute(query)
    results = c.fetchall()
        
    print(f"\n\n--- {target_month} less than 150hr ---")
    print(f"{'Room'} | {'Total Time'}")
    print("-" * 55)
        
    if not results:
        print("the database is empty")
        print("-" * 55)
    else:
        for row in results:
            room = row[0]
            time = row[1]
            print(f"{room:<10} | {time:<10.2f}")
        print("-" * 55)
                
       
    c.close()
    conn.close()
        
    

if __name__ == "__main__": 
    last_month_date = datetime.now() - relativedelta(months=1)
    Lmouth_Y =str(last_month_date.year)
    Lmouth =int(last_month_date.month)
    Uinput = input("Would you like to check the report of last month? (Y/N)")
    if Uinput =="Y":
        print_low_usage_rooms(Lmouth,Lmouth_Y)
    else:
        Uinput = input("Would you like to check the report of other month? (Y/N)")
        if Uinput =="Y":
            Lmouth_Y =str(input("Enter the year you want to check"))
            Lmouth =int(input("Enter the month you want to check in integer"))
            print_low_usage_rooms(Lmouth,Lmouth_Y)
        else:
            print("Program end")