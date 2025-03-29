import sqlite3
import os
from datetime import datetime

DB_NAME = "animals.db"


def get_db_connection():
    """Get a connection to the SQLite database."""
    return sqlite3.connect(DB_NAME)


def create_tables():
    """Create the database tables if they don't exist."""
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


# Animal CRUD Operations
def add_animal(name, species, breed, birthday, sex, castrated, weight, image_path):
    """Add a new animal to the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO animals (name, species, breed, birthday, sex, castrated, current_weight, image_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (name, species, breed, birthday, sex, castrated, weight, image_path)
        )
        animal_id = cursor.lastrowid

        # Add initial weight record to history
        today = datetime.now().strftime("%Y-%m-%d")
        add_weight_record(animal_id, today, weight)

        conn.commit()
        conn.close()
        return animal_id
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


def get_animal(animal_id):
    """Get animal details by ID."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM animals WHERE id = ?",
            (animal_id,)
        )
        animal = cursor.fetchone()
        conn.close()
        return animal
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


def update_animal(animal_id, name, species, breed, birthday, sex, castrated, weight, image_path):
    """Update an existing animal's information."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get current weight to check if it changed
        cursor.execute("SELECT current_weight FROM animals WHERE id = ?", (animal_id,))
        current_weight = cursor.fetchone()[0]

        cursor.execute(
            """UPDATE animals SET 
               name = ?, species = ?, breed = ?, birthday = ?, 
               sex = ?, castrated = ?, current_weight = ?, image_path = ?
               WHERE id = ?""",
            (name, species, breed, birthday, sex, castrated, weight, image_path, animal_id)
        )

        # If weight changed, add to history
        if weight != current_weight:
            today = datetime.now().strftime("%Y-%m-%d")
            add_weight_record(animal_id, today, weight)

        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False


def delete_animal(animal_id):
    """Delete an animal and its related records."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get image path to delete file
        cursor.execute("SELECT image_path FROM animals WHERE id = ?", (animal_id,))
        image_path = cursor.fetchone()[0]

        # Delete related records first (foreign key constraints)
        cursor.execute("DELETE FROM weight_history WHERE animal_id = ?", (animal_id,))
        cursor.execute("DELETE FROM assessments WHERE animal_id = ?", (animal_id,))

        # Delete the animal
        cursor.execute("DELETE FROM animals WHERE id = ?", (animal_id,))

        conn.commit()
        conn.close()

        # Delete image file if it exists
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except OSError as e:
                print(f"Error deleting image file: {e}")

        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False


def get_all_animals():
    """Get a list of all animals."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, species FROM animals ORDER BY name")
        animals = cursor.fetchall()
        conn.close()
        return animals
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []


def get_animals_by_species(species):
    """Get a list of animals filtered by species."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, breed FROM animals WHERE species = ? ORDER BY name",
            (species,)
        )
        animals = cursor.fetchall()
        conn.close()
        return animals
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []


# Weight History Operations
def add_weight_record(animal_id, date, weight):
    """Add a new weight record for an animal."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO weight_history (animal_id, date, weight) VALUES (?, ?, ?)",
            (animal_id, date, weight)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False


def get_weight_history(animal_id):
    """Get weight history for an animal."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT date, weight FROM weight_history WHERE animal_id = ? ORDER BY date",
            (animal_id,)
        )
        weights = cursor.fetchall()
        conn.close()
        return weights
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []


def delete_weight_record(weight_id):
    """Delete a weight record by ID."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM weight_history WHERE id = ?", (weight_id,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False


# Assessment Operations
def add_assessment(animal_id, date, scale_used, result):
    """Add a new assessment for an animal."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO assessments (animal_id, date, scale_used, result) VALUES (?, ?, ?, ?)",
            (animal_id, date, scale_used, result)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False


def get_assessments(animal_id):
    """Get assessment history for an animal."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, date, scale_used, result FROM assessments WHERE animal_id = ? ORDER BY date DESC",
            (animal_id,)
        )
        assessments = cursor.fetchall()
        conn.close()
        return assessments
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []


def delete_assessment(assessment_id):
    """Delete an assessment by ID."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM assessments WHERE id = ?", (assessment_id,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False


# Initialize database when module is imported
create_tables()