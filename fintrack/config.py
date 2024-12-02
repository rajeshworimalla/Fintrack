import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost", user="root", password="", database="fintrack"
    )
    
def get_user_info(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s AND password = %s;", (username,password))
    results = cur.fetchone()
    conn.close() 
    if results: 
        return results
    else: 
        return False

def insert_new_user(username,password,email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users(username, password, email) VALUES (%s, %s, %s)", (username, password, email))
    conn.commit()
    conn.close()

def user_exists(username, email): 
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s OR email = %s;", (username,email))
    results = cur.fetchall()
    conn.close()
    if results: 
        return True
    else: 
        return False

def add_expense(date,category,amount,description,user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO expenses(date_added, category, amount, description, user_id) VALUES (%s, %s, %s, %s, %s)", (date,category,amount,description, user_id))
    conn.commit()
    conn.close()
    
def get_expenses(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, date_added, category, amount, description FROM expenses WHERE user_id = %s", (user_id,))
    result = cur.fetchall()
    conn.close()
    return result


def add_income(date,source,amount,description,user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO incomes(date_added, source, amount, description, user_id) VALUES (%s, %s, %s, %s, %s)", (date,source,amount,description, user_id))
    conn.commit()
    conn.close()
    
def get_incomes(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, date_added, source, amount, description FROM incomes WHERE user_id = %s", (user_id,))
    result = cur.fetchall()
    conn.close()
    return result

def delete_user_expense(transaction_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id =%s",(transaction_id,))
    conn.commit()
    conn.close()

def delete_user_income(transaction_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM incomes WHERE id =%s",(transaction_id,))
    conn.commit()
    conn.close()

def get_categorized_expenses(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""SELECT category, SUM(amount) AS total
                    FROM expenses
                    WHERE user_id = %s
                    GROUP BY category""",(user_id,));
    results = cur.fetchall()
    conn.close()
    return results
