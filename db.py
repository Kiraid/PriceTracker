import os
import sqlite3
from flask import jsonify
import uuid

DB_PATH = 'users.db'


def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                username TEXT NOT NULL
            )
        ''')
        c.execute('''
            CREATE TABLE product_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                product_url TEXT NOT NULL,
                product_name TEXT NOT NULL,
                product_price REAL NOT NULL,
                percentage INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
    ''')
        
        conn.commit()
        conn.close()
        
def get_connection():
    return sqlite3.connect(DB_PATH)         


def register_user(email, hashed_password, username):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (email, password, username) VALUES (?, ?, ?)", (email, hashed_password, username))
        conn.commit()
        user_id = c.lastrowid
        return jsonify({"message": "User registered", "user_id": user_id}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409
    finally:
        conn.close()
    
def login_user(email):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, username, password FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return user
        
        
def insert_new_price(user_id, product_name, product_url, product_price, product_id , percentage):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO product_tracking (product_id ,user_id, product_url, product_name,  product_price, percentage) VALUES (?, ?, ?, ?, ?, ?)",
          (product_id ,user_id, product_url, product_name ,product_price, percentage))
        conn.commit()
        conn.close()  
        return
    except:
        conn.close()
        return 
    
def add_product_to_tracking(user_id, product_name, product_url, product_price, percentage):
    conn = get_connection()
    c = conn.cursor()
    product_id = str(uuid.uuid4())  # or use uuid.uuid4().hex for shorter form
    try:
        c.execute("""
            INSERT INTO product_tracking (product_id, user_id, product_name, product_url, product_price, percentage)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (product_id, user_id, product_name, product_url, product_price, percentage))
        conn.commit()
        conn.close()
        return product_id
    except Exception as e:
        conn.close()
        print(f"Error adding product: {e}")
        return ""
    
def get_latest_products_all():
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            SELECT pt.*
            FROM product_tracking pt
            JOIN (
                SELECT product_id, MAX(timestamp) as max_time
                FROM product_tracking
                GROUP BY product_id
            ) grouped_pt
            ON pt.product_id = grouped_pt.product_id AND pt.timestamp = grouped_pt.max_time
        """)
        products = c.fetchall()
        conn.close()
        return products
    except Exception as e:
        conn.close()
        print(f"Error: {e}")
        return []
    
    
def get_all_user_products(user_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            SELECT pt.product_name, pt.product_id, pt.product_price
            FROM product_tracking pt
            JOIN (
                SELECT product_id, MAX(timestamp) as max_time
                FROM product_tracking
                GROUP BY product_id
            ) grouped_pt
            ON pt.product_id = grouped_pt.product_id AND pt.timestamp = grouped_pt.max_time
            WHERE pt.user_id = ?
        """, (user_id,))
        result = c.fetchall()
        return result
    except Exception as e:
        print(f"Error: {e}")
        return [] 
    
def get_all_product_entries(product_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT timestamp, product_name, product_price FROM product_tracking WHERE product_id = ?", (product_id,))
        entries = c.fetchall()
        return entries
    except Exception as e:
        print(f"Error: {e}")
        return []           