from flask import Flask, jsonify, request
from connexion import connexion

app = Flask(__name__)

@app.route("/")
def home():
    return {"status": "Backend OK"}

@app.route("/leaderboard")
def leaderboard():
    with connexion() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, coins
            FROM PLAYERS
            JOIN PLAYER_STATS USING(player_id)
            ORDER BY coins DESC
            LIMIT 20
        """)
        rows = cursor.fetchall()
        return jsonify([dict(row) for row in rows])

@app.route("/create-test-user", methods=["POST"])
def create_test_user():
    data = request.json
    username = data.get("username")

    with connexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO PLAYERS (username, created_at) VALUES (?, ?)",
            (username, 0)
        )
        player_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO PLAYER_STATS (player_id, coins) VALUES (?, ?)",
            (player_id, 0)
        )
        conn.commit()

    return {"created": username}