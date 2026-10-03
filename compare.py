import sqlite3
import time
from datetime import datetime

from dateutil.relativedelta import relativedelta


mouthN = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",
          5:"May",6:"Jun",7:"Jul",8:"Aug",9:
          "Sep",10:"Oct",11:"Nov",12:"Dec"}

def table_exists(db_path, table_name):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query the sqlite_master table for the specific table name
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name=(?);"
    cursor.execute(query, (table_name,))
    
    # fetchone() returns the row if found, or None if not
    result = cursor.fetchone()

    conn.close()
    return result is not None

def compara(ID:str,tmouth:int,year:str):
    #initialization, transfroming and finding data for time calcultion
    TTime = 0
    tmouth= mouthN[tmouth]
    
    
    ET =[]
    RNE= []
    LT =[]
    RNL= []
    time_format = "%Y-%m-%d %H:%M" #set format for calculation

    #find record form database
    conn = sqlite3.connect('database_pkpd.db')
    c = conn.cursor()
    #find user's entry time and record number from entry table
    c.execute("SELECT ENTRY_TIME, REC_Number FROM REC_ENTRY WHERE YEAR_E= (?) AND MOUTH_E = (?) AND RES_ID = (?)",(year,tmouth,ID,))
    EntryL = c.fetchall()
    i=0
    
    #transform to two list
    for row1 in EntryL:
        ET.append(datetime.strptime(row1[0],time_format))#contain the time
        RNE.append(row1[1])#contain the record_Number
        i +=1
        

    #find user's leave time and record number from entry table
    c.execute("SELECT LEAVE_TIME, REC_Number FROM REC_LEAVE WHERE YEAR_L = (?) AND MOUTH_L = (?) AND RES_ID = (?)",(year,tmouth,ID,))
    LeaveL = c.fetchall()
    i =0
    #transform to two list
    for row2 in LeaveL:
        LT.append(datetime.strptime(row2[0],time_format))#contain the time
        RNL.append(row2[1])#contain the record_Number
        i +=1
        
    conn.close()
   #calculate time different
    
  
    #calculate time different
    for i in range(len(LT)):
        
        #if RNE[i] == RNL[i] and str(i+1) in RNE[i]:
        Time_diff = LT[i] - ET[i]
        TTime += float(Time_diff.total_seconds()/3600)
        
        
        
           
        
    return  TTime# return the total time different

def creat_table(year:str,mouth:int):
    TabName = f"{mouth}_{year}"
    conn = sqlite3.connect('database_pkpd.db')
    c = conn.cursor()
    sqlcom = f"CREATE TABLE IF NOT EXISTS {TabName} (RES_ID TEXT, RES_NAME TEXT, RES_ROOM TEXT, Total_Time REAL)"
    c.execute(sqlcom)
    conn.commit()
    conn.close()
    return TabName

def gen_rep(year:str,tmouth:int):
    mouth = mouthN[tmouth]
    conn = sqlite3.connect('database_pkpd.db')
    c = conn.cursor()
    #find resident user's id, name, room
    c.execute("SELECT RES_ID, RES_NAME, RES_ROOM FROM Info WHERE living = 1 ")
    InfoL = c.fetchall()
    conn.close
    ID=[]
    NAME =[]
    ROOM = []
    ttime =[]
    i =0 
    TabName = f"{mouth}_{year}"

    if table_exists('database_pkpd.db', TabName) == False:
        creat_table(year,mouth)
    else:
        conn = sqlite3.connect('database_pkpd.db')
        c = conn.cursor()
        query = f"DROP TABLE IF EXISTS {TabName}"
        c.execute(query)
        creat_table(year,mouth)
        conn.commit()
        conn.close()
    #transform to three list
    for row2 in InfoL:
        ID.insert(i,row2[0])#contain the time
        NAME.insert(i,row2[1])#contain the record_Number
        ROOM.insert(i,row2[2])#contain the record_Number
        i +=1
    
    for j in range(i):
        ttime.append(compara(ID[j],tmouth,year))
        #print(ID[j],NAME[j],ROOM[j],ttime[j])

    conn = sqlite3.connect('database_pkpd.db')
    c = conn.cursor()
    
    
    for k in range(i):#store the data into database
        sqlcom = f"INSERT INTO {TabName} (RES_ID, RES_Name, RES_ROOM, Total_Time) VALUES ('{ID[k]}','{NAME[k]}','{ROOM[k]}',{ttime[k]})"
        c.execute(sqlcom)
  
    conn.commit()
    conn.close
    print("report done")
if __name__ == "__main__":
    last_month_date = datetime.now() - relativedelta(months=1)
    Lmouth_Y =str(last_month_date.year)
    Lmouth =int(last_month_date.month)
    
    Uinput = input("Would you like to check the report of last month? (Y/N)")
    if Uinput =="Y":
        gen_rep(Lmouth_Y,Lmouth)
    else:
        Uinput = input("Would you like to check the report of other month? (Y/N)")
        if Uinput =="Y":
            Lmouth_Y =str(input("Enter the year you want to check"))
            Lmouth =int(input("Enter the month you want to check in integer"))
            gen_rep(Lmouth_Y,Lmouth)
        else:
            print("Program end")