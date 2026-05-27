from flask import Flask, request, jsonify, session, send_from_directory
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import mysql.connector
from datetime import datetime

app = Flask(__name__, static_folder='static')

app.secret_key = "mysecret123"

app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

bcrypt = Bcrypt(app)

CORS(app, supports_credentials=True)

# ---------------- DATABASE ----------------

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root@1432",
    database="expense_tracker"
)

cursor = db.cursor(dictionary=True)

# ---------------- HTML ROUTES ----------------

@app.route('/')
def login_page():
    return send_from_directory('static', 'login.html')


@app.route('/register.html')
def register_page():
    return send_from_directory('static', 'register.html')


@app.route('/dashboard.html')
def dashboard_page():
    return send_from_directory('static', 'dashboard.html')


@app.route('/expenses.html')
def expenses_page():
    return send_from_directory('static', 'expenses.html')

# ---------------- HOME ----------------

@app.route('/')
def home():
    return send_from_directory('static', 'login.html')

# ---------------- REGISTER ----------------

@app.route('/register', methods=['POST'])
def register():

    try:

        data = request.get_json()

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # ---------------- CHECK EMPTY ----------------

        if username == "" or email == "" or password == "":
            return jsonify({
                "message": "Please fill all fields"
            }), 400

        # ---------------- CHECK USER EXISTS ----------------

        query = """
        SELECT * FROM users
        WHERE email=%s
        """

        cursor.execute(query, (email,))

        existing_user = cursor.fetchone()

        if existing_user:

            return jsonify({
                "message": "Email already exists"
            }), 400

        # ---------------- HASH PASSWORD ----------------

        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode('utf-8')

        # ---------------- INSERT USER ----------------

        insert_query = """
        INSERT INTO users
        (username, email, password)
        VALUES (%s, %s, %s)
        """

        values = (
            username,
            email,
            hashed_password
        )

        cursor.execute(insert_query, values)

        db.commit()

        return jsonify({
            "message": "Registration Successful"
        }), 201

    except Exception as e:

        print("REGISTER ERROR:", e)

        return jsonify({
            "message": "Registration Failed"
        }), 500
# ---------------- LOGIN ----------------
@app.route('/login', methods=['POST'])
def login():

    try:

        data = request.get_json()

        email = data.get('email')
        password = data.get('password')

        # ---------------- VALIDATION ----------------

        if not email or not password:
            return jsonify({
                "message": "Email and Password required"
            }), 400

        # ---------------- FIND USER ----------------

        query = "SELECT * FROM users WHERE email=%s"

        cursor.execute(query, (email,))

        user = cursor.fetchone()

        # ---------------- CHECK USER ----------------

        if not user:
            return jsonify({
                "message": "User not found"
            }), 401

        # ---------------- CHECK PASSWORD ----------------

        if not bcrypt.check_password_hash(
            user['password'],
            password
        ):
            return jsonify({
                "message": "Incorrect Password"
            }), 401

        # ---------------- CREATE SESSION ----------------

        session['user_id'] = user['id']
        session['username'] = user['username']

        session.permanent = True

        return jsonify({
            "message": "Login Successful",
            "username": user['username']
        }), 200

    except Exception as e:

        print("LOGIN ERROR:", e)

        return jsonify({
            "message": "Login Failed"
        }), 500
# ---------------- LOGOUT ----------------

@app.route('/logout')
def logout():

    session.clear()

    return jsonify({
        "message":"Logged out successfully"
    }), 200

# ---------------- CHECK LOGIN ----------------

def check_login():
    return 'user_id' in session

# ---------------- GET EXPENSES ----------------

@app.route('/expenses', methods=['GET'])
def get_expenses():

    if not check_login():
        return jsonify({"message": "Unauthorized"}), 401

    query = """
    SELECT * FROM expenses
    WHERE user_id=%s
    ORDER BY date DESC
    """

    cursor.execute(query, (session['user_id'],))
    expenses = cursor.fetchall()

    return jsonify(expenses)

# ---------------- ADD EXPENSE ----------------

@app.route('/expenses', methods=['POST'])
def add_expense():

    if not check_login():
        return jsonify({"message": "Unauthorized"}), 401

    data = request.json

    title = data['title']
    amount = float(data['amount'])
    category = data['category']
    date = data['date']
    note = data.get('note', '')

    if amount <= 0:
        return jsonify({"message": "Amount must be positive"}), 400

    try:
        datetime.strptime(date, '%Y-%m-%d')
    except:
        return jsonify({"message": "Invalid date"}), 400

    query = """
    INSERT INTO expenses
    (user_id,title,amount,category,date,note)
    VALUES (%s,%s,%s,%s,%s,%s)
    """

    values = (
        session['user_id'],
        title,
        amount,
        category,
        date,
        note
    )

    cursor.execute(query, values)
    db.commit()

    return jsonify({"message": "Expense Added"}), 201

# ---------------- UPDATE EXPENSE ----------------

@app.route('/expenses/<int:id>', methods=['PUT'])
def update_expense(id):

    if not check_login():
        return jsonify({"message": "Unauthorized"}), 401

    data = request.json

    query = """
    UPDATE expenses
    SET title=%s, amount=%s, category=%s, date=%s, note=%s
    WHERE id=%s AND user_id=%s
    """

    values = (
        data['title'],
        data['amount'],
        data['category'],
        data['date'],
        data['note'],
        id,
        session['user_id']
    )

    cursor.execute(query, values)
    db.commit()

    return jsonify({"message": "Expense Updated"})

# ---------------- DELETE EXPENSE ----------------

@app.route('/expenses/<int:id>', methods=['DELETE'])
def delete_expense(id):

    if not check_login():
        return jsonify({"message": "Unauthorized"}), 401

    query = """
    DELETE FROM expenses
    WHERE id=%s AND user_id=%s
    """

    cursor.execute(query, (id, session['user_id']))
    db.commit()

    return jsonify({"message": "Expense Deleted"})

# ---------------- SUMMARY ----------------

@app.route('/expenses/summary')
def summary():

    if not check_login():
        return jsonify({"message": "Unauthorized"}), 401

    user_id = session['user_id']

    cursor.execute(
        "SELECT SUM(amount) AS total FROM expenses WHERE user_id=%s",
        (user_id,)
    )
    total = cursor.fetchone()['total'] or 0

    cursor.execute(
        "SELECT MAX(amount) AS highest FROM expenses WHERE user_id=%s",
        (user_id,)
    )
    highest = cursor.fetchone()['highest'] or 0

    cursor.execute(
        "SELECT COUNT(*) AS count FROM expenses WHERE user_id=%s",
        (user_id,)
    )
    count = cursor.fetchone()['count']

    cursor.execute("""
    SELECT category, SUM(amount) AS total
    FROM expenses
    WHERE user_id=%s
    GROUP BY category
    """, (user_id,))

    categories = cursor.fetchall()

    return jsonify({
        "username": session['username'],
        "total": total,
        "highest": highest,
        "count": count,
        "categories": categories
    })

# ---------------- FILTER ----------------

@app.route('/expenses/filter')
def filter_expenses():

    if not check_login():
        return jsonify({"message": "Unauthorized"}), 401

    category = request.args.get('category')
    from_date = request.args.get('from')
    to_date = request.args.get('to')

    query = "SELECT * FROM expenses WHERE user_id=%s"
    values = [session['user_id']]

    if category:
        query += " AND category=%s"
        values.append(category)

    if from_date and to_date:
        query += " AND date BETWEEN %s AND %s"
        values.extend([from_date, to_date])

    cursor.execute(query, tuple(values))

    expenses = cursor.fetchall()

    return jsonify(expenses)

# ---------------- RUN ----------------

if __name__ == '__main__':
    app.run(debug=True)