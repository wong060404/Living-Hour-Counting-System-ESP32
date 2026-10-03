import sqlite3
import time
def find_EC(ID):
    sid= str(ID)
    conn = sqlite3.connect('database_pkpd.db')
    c = conn.cursor()
    ec = c.execute("SELECT ENTRY_COUNT FROM Info WHERE Resident_ID = (?)", (sid,))
    conn.close
    return ec

def EC_upgdate(ID, cec):
    sid= str(ID)
    nec= cec +1
    conn = sqlite3.connect('database_pkpd.db')
    c = conn.cursor()
    c.execute("UPDATE Info set ENTRY_COUNT = (?) WHERE Resident_ID = (?)", (nec, sid,))
    conn.commit()
    conn.close


def sql_input(ID,Name):
    RT = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    mouth= time.strftime("%b")
    ec = find_EC(ID)
    for row in ec:
        ecstr =(row[0])
    record_id=f"{Name}_{mouth}_{ecstr}"

    conn = sqlite3.connect('database_pkpd.db')
    c = conn.cursor()
    c.execute("INSERT INTO RECORD_ENTRY (Resident_ID,Resident_Name, ENTRY_TIME, RECORD_Number) VALUES (?, ? ,?, ?)",(ID, Name,RT,record_id,))
    conn.commit()
    conn.close
    cec = int(ecstr)
    EC_upgdate(ID, cec)

def sql_inputL(ID,Name):
    RT = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    mouth= time.strftime("%b")
    ec = find_EC(ID)
    for row in ec:
        ecstr =(row[0])
    cec = int(ecstr)
    cec =cec -1
    record_id=f"{Name}_{mouth}_{cec}"
    
    conn = sqlite3.connect('database_pkpd.db')
    c = conn.cursor()
    c.execute("INSERT INTO Record_LEAVE (Resident_ID,Resident_Name, LEAVE_TIME, Record_Number) VALUES (?, ? ,?, ?)",(ID, Name,RT,record_id,))
    conn.commit()
    conn.close
    
    

sql_input(1, "kailas")
sql_inputL(1, "kailas")
