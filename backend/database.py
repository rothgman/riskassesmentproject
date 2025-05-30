import sqlite3

def connect_db():
    return sqlite3.connect("microloan.db")

def init_db():
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS borrowers (
            id TEXT PRIMARY KEY,
            name TEXT,
            region TEXT,
            loan_amount REAL,
            base_score REAL,
            adjusted_score REAL,
            risk TEXT,
            decision TEXT
        )
    ''')
    
    
    c.execute('SELECT COUNT(*) FROM borrowers')
    if c.fetchone()[0] == 0:
        sample_data = [
            ('1', 'Maria Johnson', 'Montserrado', 500.0, 72.5, 75.0, 'Medium', 'Approved'),
            ('2', 'James Cooper', 'Bong', 1200.0, 65.0, 68.0, 'Medium', 'Conditional'),
            ('3', 'Sarah Williams', 'Nimba', 300.0, 85.0, 87.0, 'Low', 'Approved')
        ]
        c.executemany('''
            INSERT INTO borrowers (id, name, region, loan_amount, base_score, adjusted_score, risk, decision)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_data)
    
    conn.commit()
    conn.close()

def get_all_borrowers():
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM borrowers")
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "name": r[1],
            "region": r[2],
            "loan_amount": r[3],
            "base_score": r[4],
            "adjusted_score": r[5],
            "risk": r[6],
            "decision": r[7]
        } for r in rows
    ]
