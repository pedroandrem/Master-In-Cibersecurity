import sqlite3
from sqlite3 import Connection, Cursor
from typing import Optional
from utils import CertificateAuthorityClient

DB_PATH: str = "database/database.db"


def get_or_create_cert(username: str, public_pem: str) -> str:
    
    conn: Connection = sqlite3.connect(DB_PATH)
    cursor: Cursor = conn.cursor()
    
    cursor.execute("""
        SELECT cert FROM users
        WHERE username = ? AND pubkey = ?
    """, (username, public_pem))
    
    result: Optional[tuple[str]] = cursor.fetchone()
    
    if result:
        conn.close()
        print("Certificate found in database.")
        return result[0]
    else:
        ca: CertificateAuthorityClient = CertificateAuthorityClient()
        new_cert: str = ca.register(public_pem)
        
        cursor.execute("""
            INSERT INTO users (username, pubkey, cert)
            VALUES (?, ?, ?)
        """, (username, public_pem, new_cert))
        conn.commit()
        conn.close()
        
        print("New certificate generated and stored in database.")
        return new_cert
