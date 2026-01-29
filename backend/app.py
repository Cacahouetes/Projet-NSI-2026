from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

DATABASE = "database.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(debug=True)