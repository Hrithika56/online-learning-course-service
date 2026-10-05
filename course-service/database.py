import sqlite3

DATABASE = "course.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            instructor TEXT NOT NULL,
            category TEXT,
            duration INTEGER,
            price REAL,
            status TEXT DEFAULT 'Active'
        )
    """)

    connection.commit()
    connection.close()