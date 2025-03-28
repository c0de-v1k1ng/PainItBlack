import sqlite3

DB_NAME = "animals.db"

def get_db_connection():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS animals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            species TEXT NOT NULL,
            breed TEXT,
            birthday TEXT,
            sex TEXT CHECK(sex IN ('Male', 'Female')),
            castrated TEXT CHECK(castrated IN ('Yes','No')),
            current_weight REAL,
            image_path TEXT
        )
    ''')


    cursor.execute('''
               CREATE TABLE IF NOT EXISTS weight_history (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   animal_id INTEGER,
                   date TEXT NOT NULL,
                   weight REAL NOT NULL,
                   FOREIGN KEY (animal_id) REFERENCES animals(id)
               )
           ''')

    cursor.execute('''
               CREATE TABLE IF NOT EXISTS assessments (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   animal_id INTEGER,
                   date TEXT NOT NULL,
                   scale_used TEXT NOT NULL,
                   result TEXT NOT NULL,
                   FOREIGN KEY (animal_id) REFERENCES animals(id)
               )
           ''')
    conn.commit()
    conn.close()

def add_animal(name, species, breed, birthday, sex, castrated, weight, image_path):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO animals (name, species, breed, birthday, sex, castrated, current_weight, image_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (name, species, breed, birthday, sex, castrated, weight, image_path)
    )
    conn.commit()
    conn.close()

create_tables()