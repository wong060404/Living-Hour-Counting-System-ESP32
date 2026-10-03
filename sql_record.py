import sqlite3
import time
from datetime import datetime

def registeruser(name:str):
    room_ID = input("Enter your room?")
    
    # 1. Connect to the SQLite database
    conn = sqlite3.connect('database_pkpd.db')
    cursor = conn.cursor()

    # 2. Execute a query to count occurrences of the specific room
    # We use a parameterized query (?) to prevent SQL injection
    query = "SELECT COUNT(*) FROM Info WHERE RES_ROOM = ? AND living = 1"
    cursor.execute(query, (room_ID,))

    # 3. Fetch the result
    # fetchone() returns a tuple, e.g., (5,)
    count = cursor.fetchone()[0]
    count = count +1
    res_ID = f"{room_ID}{count:02}"
    query = "INSERT INTO Info (RES_ID, RES_NAME, RES_ROOM, living, ENTRY_COUNT, LEAVE_COUNT) VALUES(?,?,?, 1, 0, 0)"
    cursor.execute(query, (res_ID, name, room_ID))
    conn.commit()
    conn.close()
    
def find_EC(ID):
    sid= str(ID)
    EC =[]
    conn = sqlite3.connect('database_pkpd.db')
    c = conn.cursor()
   
    ec =c.execute("SELECT ENTRY_COUNT FROM Info WHERE RES_ID = (?)", (sid,))
    for row in ec:
        EC.append(row[0])
    
    conn.close
    return EC[0]
    

def find_LC(ID):
    sid= str(ID)
    LC =[]
    conn = sqlite3.connect('database_pkpd.db')
    c = conn.cursor()
   
    lc =c.execute("SELECT LEAVE_COUNT FROM Info WHERE RES_ID = (?)", (sid,))
    for row in lc:
        LC.append(row[0])
    conn.close
    return LC[0]
    

def EC_upgdate(ID, cec):
    sid= str(ID)
    nec= cec
    conn = sqlite3.connect('database_pkpd.db')
    c = conn.cursor()
    c.execute("UPDATE Info set ENTRY_COUNT = (?) WHERE RES_ID = (?)", (nec, sid,))
    conn.commit()
    conn.close

def LC_upgdate(ID, cec):
    sid= str(ID)
    nec= cec
    conn = sqlite3.connect('database_pkpd.db')
    c = conn.cursor()
    c.execute("UPDATE Info set LEAVE_COUNT = (?) WHERE RES_ID = (?)", (nec, sid,))
    conn.commit()
    conn.close

def sql_inputE(ID):
    #lond data for storing
    RT = time.strftime("%Y-%m-%d %H:%M",time.localtime())
    mouth= time.strftime("%b")
    year = time.strftime("%Y")
    #find Entry count
    ec = find_EC(ID)
    cec = int(ec)
    cec =cec +1
    #format the record_id
    record_id=f"{ID}_{year}_{mouth}_{cec}"
    # save user entry record to database
    conn = sqlite3.connect('database_pkpd.db')
    c = conn.cursor()
    c.execute("INSERT INTO REC_ENTRY (RES_ID,  ENTRY_TIME, REC_Number, YEAR_E, MOUTH_E) VALUES (?,?, ?, ?, ?)",(ID, RT,record_id,year, mouth,))
    conn.commit()
    conn.close
    #updata the entry count
    cec = int(cec)
    EC_upgdate(ID, cec)

def sql_inputL(ID):
    #lond data for storing
    RT = time.strftime("%Y-%m-%d %H:%M",time.localtime())
    mouth= time.strftime("%b")
    year = time.strftime("%Y")
    #find Entry count
    lc = find_LC(ID)
    clc = int(lc)
    clc =clc +1
    #format the record_id
    record_id=f"{ID}_{year}_{mouth}_{clc}"
    #save user leave record to database
    conn = sqlite3.connect('database_pkpd.db')
    c = conn.cursor()
    c.execute("INSERT INTO REC_LEAVE (RES_ID,  LEAVE_TIME, REC_Number, YEAR_L, MOUTH_L) VALUES (?,?, ?, ?, ?)",(ID, RT,record_id,year,mouth,))
    conn.commit()
    conn.close
    #updata the leave count
    clc = int(clc)
    LC_upgdate(ID, clc)

def sql_input_select(name:str):
    ID = find_resID(name)
    ec =find_EC(ID)
    lc =find_LC(ID)
    if ec ==lc:
        sql_inputE(ID)
    elif ec > lc:
        sql_inputL(ID)
    else:
        print("the database have error")

def find_resID(name:str):
    conn = sqlite3.connect('database_pkpd.db')
    c = conn.cursor()
    sqlcom = f"SELECT RES_ID FROM Info WHERE RES_NAME = '{name}'"
    c.execute(sqlcom)
    name = c.fetchone()
    conn.close()
    return name [0]

if __name__ == "__main__":   
    print("testing")
    #sql_inputE("2","alex")
    #sql_inputL("2","alex")
    #print(compara("1","Mar","2026"))
    #print(compara("2","Mar","2026"))
    #gen_rep("2026",3)
    #creat_table("2026","Mar")
    #sql_input_select("kailas")
    #print(find_EC(1))
    #print(find_LC(1))
    registeruser("test1")
    