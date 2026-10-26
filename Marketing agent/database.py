import sqlite3
from datetime import datetime

DB_FILE = "leads_engine.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,            -- indiamart, gmail, instagram, facebook, youtube, website
            sender_name TEXT,
            contact_info TEXT,      -- phone or email
            query TEXT,
            ai_reply TEXT,
            status TEXT DEFAULT 'New',
            landing_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel TEXT,           -- whatsapp, sms, email
            recipient TEXT,
            message TEXT,
            status TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_lead(source: str, name: str, contact: str, query: str, ai_reply: str, landing_url: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leads (source, sender_name, contact_info, query, ai_reply, landing_url)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (source, name, contact, query, ai_reply, landing_url))
    conn.commit()
    conn.close()

def get_all_leads():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads ORDER BY created_at DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def log_campaign(channel: str, recipient: str, message: str, status: str = "Sent"):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO campaigns (channel, recipient, message, status)
        VALUES (?, ?, ?, ?)
    """, (channel, recipient, message, status))
    conn.commit()
    conn.close()

def get_all_campaigns():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM campaigns ORDER BY sent_at DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows