from flask import Flask, render_template, request, redirect, session, jsonify
import mysql.connector
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


# ---------------- DATABASE CONNECTION ----------------

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


# ---------------- HOME ----------------

@app.route("/")
def home():
    if "user_id" in session:
        return redirect("/dashboard")

    return redirect("/login")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        db = get_db_connection()
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO users(name, email, password)
                VALUES(%s, %s, %s)
                """,
                (name, email, hashed_password)
            )

            db.commit()

        except mysql.connector.Error:
            return "Email already exists!"

        finally:
            cursor.close()
            db.close()

        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            return redirect("/dashboard")

        return "Invalid email or password"

    return render_template("login.html")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        name=session["user_name"]
    )


# ---------------- ADD TRANSACTION ----------------

@app.route("/add_transaction", methods=["POST"])
def add_transaction():

    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json

    transaction_type = data["type"]
    category = data["category"]
    amount = data["amount"]
    description = data["description"]

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO transactions
        (user_id, type, category, amount, description, transaction_date)
        VALUES(%s, %s, %s, %s, %s, %s)
        """,
        (
            session["user_id"],
            transaction_type,
            category,
            amount,
            description,
            date.today()
        )
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Transaction added successfully"})


# ---------------- GET TRANSACTIONS ----------------

@app.route("/transactions")
def transactions():

    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT * FROM transactions
        WHERE user_id=%s
        ORDER BY transaction_date DESC
        """,
        (session["user_id"],)
    )

    data = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(data)


# ---------------- DELETE TRANSACTION ----------------

@app.route("/delete_transaction/<int:id>", methods=["DELETE"])
def delete_transaction(id):

    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        DELETE FROM transactions
        WHERE id=%s AND user_id=%s
        """,
        (id, session["user_id"])
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Transaction deleted"})


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# ---------------- RUN APPLICATION -----------------
