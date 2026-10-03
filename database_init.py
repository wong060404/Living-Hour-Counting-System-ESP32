import sqlite3
def build_empty_database():
    db_name='database_pkpd.db'
    # Connect to the database (creates it if it doesn't exist)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # 1. Create the 'Info' table 
    c.execute('''
        CREATE TABLE IF NOT EXISTS Info (
            RES_ID TEXT,
            RES_NAME TEXT NOT NULL,
            RES_ROOM TEXT,
            ENTRY_COUNT INTEGER,
            LEAVE_COUNT INTEGER,
            living INTEGER DEFAULT ('0')
        )
    ''')

    # 2. Create the 'REC_ENTRY' table 
    c.execute('''
        CREATE TABLE IF NOT EXISTS REC_ENTRY (
            RES_ID TEXT,
            REC_Number TEXT,
            ENTRY_TIME,
            YEAR_E TEXT,
            MOUTH_E TEXT
        )
    ''')

    # 3. Create the 'REC_LEAVE' table 
    c.execute('''
        CREATE TABLE IF NOT EXISTS REC_LEAVE (
            RES_ID TEXT,
            REC_Number TEXT,
            LEAVE_TIME TEXT,
            YEAR_L TEXT,
            MOUTH_L TEXT
        )
    ''')

   

    

    # Commit changes and close connection
    conn.commit()
    conn.close()
    print(f"database '{db_name}' has been built successfully.")

if __name__ == "__main__":
    build_empty_database()