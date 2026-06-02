import os
import mysql.connector
from mysql.connector import Error


def get_connection():
    return mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST', 'localhost'),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', ''),
        database=os.environ.get('MYSQL_DATABASE', 'tasksdb')
    )


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()


def get_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM tasks ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


def add_task(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tasks (name) VALUES (%s)', (name,))
    conn.commit()
    cursor.close()
    conn.close()
