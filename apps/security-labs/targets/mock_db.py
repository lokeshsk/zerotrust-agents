import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI(title="Vulnerable Mock DB", version="1.0")

DB_FILE = "sandbox.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Create a dummy users table with PII
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            ssn TEXT NOT NULL
        )
    ''')
    # Clear and re-seed
    cursor.execute('DELETE FROM users')
    
    dummy_users = [
        (1, 'Alice Smith', 'alice@example.com', '123-45-6789'),
        (2, 'Bob Jones', 'bob@example.com', '987-65-4321'),
        (3, 'Charlie Brown', 'charlie@example.com', '555-00-1111')
    ]
    cursor.executemany('INSERT INTO users VALUES (?, ?, ?, ?)', dummy_users)
    conn.commit()
    conn.close()

@app.on_event("startup")
def startup_event():
    init_db()
    print("Mock DB initialized with dummy PII data.")

class QueryRequest(BaseModel):
    sql: str

@app.post("/execute_sql")
def execute_sql(payload: QueryRequest):
    """
    VULNERABLE ENDPOINT: Blindly executes whatever SQL the agent sends.
    This is intentionally insecure for testing the ZTA Firewall.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Danger! Direct execution of arbitrary SQL
        cursor.executescript(payload.sql)
        conn.commit()
        
        # If it was a SELECT query, fetch results
        if payload.sql.strip().upper().startswith("SELECT"):
            cursor.execute(payload.sql)
            results = cursor.fetchall()
            conn.close()
            return {"status": "success", "data": results}
            
        conn.close()
        return {"status": "success", "message": "Query executed."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/reset")
def reset_sandbox():
    """Resets the mock database back to its original state."""
    init_db()
    return {"status": "success", "message": "Sandbox reset."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
