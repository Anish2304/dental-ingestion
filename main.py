from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, os

app = Flask(__name__)
CORS(app)
DB = "patients.db"

def get_db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with get_db() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                PatNum     INTEGER PRIMARY KEY AUTOINCREMENT,
                FName      TEXT,
                LName      TEXT,
                MiddleI    TEXT,
                Birthdate  TEXT,
                SSN        TEXT,
                HmPhone    TEXT,
                Address    TEXT,
                City       TEXT,
                State      TEXT,
                Zip        TEXT,
                Email      TEXT,
                priProvAbbr TEXT,
                PatStatus  TEXT DEFAULT 'Patient',
                BillingType TEXT DEFAULT 'Standard Account'
            )
        """)
        # Seed a few rows if empty
        if con.execute("SELECT COUNT(*) FROM patients").fetchone()[0] == 0:
            con.executemany(
                "INSERT INTO patients (FName,LName,Birthdate,SSN,HmPhone,Address,City,State,Zip,Email,priProvAbbr) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                [
                    ("Alice","Smith","1985-03-12","123-45-6789","(555)100-0001","10 Elm St","Hartford","CT","06101","alice@example.com","DOC1"),
                    ("Bob",  "Jones","1990-07-24","987-65-4321","(555)100-0002","20 Oak Ave","Boston","MA","02101","bob@example.com","DOC2"),
                    ("Carol","Lee",  "1978-11-05","555-44-3333","(555)100-0003","30 Pine Rd","New York","NY","10001","carol@example.com","DOC1"),
                ]
            )

@app.get("/api/patients")
def list_patients():
    with get_db() as con:
        rows = con.execute("SELECT * FROM patients ORDER BY PatNum DESC").fetchall()
    return jsonify([dict(r) for r in rows])

@app.post("/api/patients")
def create_patient():
    d = request.json or {}
    if not d.get("FName") or not d.get("LName"):
        return jsonify({"error": "FName and LName required"}), 400
    with get_db() as con:
        cur = con.execute(
            """INSERT INTO patients (FName,LName,MiddleI,Birthdate,SSN,HmPhone,Address,City,State,Zip,Email,priProvAbbr,PatStatus,BillingType)
               VALUES (:FName,:LName,:MiddleI,:Birthdate,:SSN,:HmPhone,:Address,:City,:State,:Zip,:Email,:priProvAbbr,:PatStatus,:BillingType)""",
            {k: d.get(k, "") for k in ("FName","LName","MiddleI","Birthdate","SSN","HmPhone","Address","City","State","Zip","Email","priProvAbbr","PatStatus","BillingType")}
        )
        row = con.execute("SELECT * FROM patients WHERE PatNum=?", (cur.lastrowid,)).fetchone()
    return jsonify(dict(row)), 201

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)