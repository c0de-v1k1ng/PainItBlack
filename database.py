import sqlite3
import os
import logging
from datetime import datetime
from contextlib import contextmanager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("database.log"), logging.StreamHandler()]
)
logger = logging.getLogger("database")

DB_NAME = "animals.db"


@contextmanager
def get_db_connection():
    """Context manager for database connections to ensure proper closing."""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        # Enable foreign key support
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def execute_query(query, params=(), fetch_mode=None):
    """
    Execute a database query with proper connection handling and error management.

    Args:
        query (str): SQL query to execute
        params (tuple): Parameters for the query
        fetch_mode (str): 'one', 'all', or None for no fetch (for INSERT/UPDATE)

    Returns:
        The query result based on fetch_mode, or True/False for success on non-fetch operations
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)

            if fetch_mode == 'one':
                return cursor.fetchone()
            elif fetch_mode == 'all':
                return cursor.fetchall()
            else:
                conn.commit()
                if cursor.lastrowid:
                    return cursor.lastrowid
                return True
    except sqlite3.Error as e:
        logger.error(f"Query execution error: {e}\nQuery: {query}\nParams: {params}")
        return None if fetch_mode else False


def create_tables():
    """Create the database tables if they don't exist."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Animals table
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
                    image_path TEXT,
                    target_weight REAL,
                    target_date TEXT
                )
            ''')

            # Weight history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weight_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    animal_id INTEGER,
                    date TEXT NOT NULL,
                    weight REAL NOT NULL,
                    FOREIGN KEY (animal_id) REFERENCES animals(id) ON DELETE CASCADE
                )
            ''')

            # Assessments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    animal_id INTEGER,
                    date TEXT NOT NULL,
                    scale_used TEXT NOT NULL,
                    result TEXT NOT NULL,
                    FOREIGN KEY (animal_id) REFERENCES animals(id) ON DELETE CASCADE
                )
            ''')

            # Check for schema updates needed
            cursor.execute("PRAGMA table_info(animals)")
            columns = [col[1] for col in cursor.fetchall()]

            if 'target_weight' not in columns:
                cursor.execute('ALTER TABLE animals ADD COLUMN target_weight REAL')
                logger.info("Added target_weight column to animals table")

            if 'target_date' not in columns:
                cursor.execute('ALTER TABLE animals ADD COLUMN target_date TEXT')
                logger.info("Added target_date column to animals table")

            conn.commit()
            logger.info("Database tables created or verified successfully")
            return True
    except sqlite3.Error as e:
        logger.error(f"Error creating tables: {e}")
        return False


# Animal CRUD Operations
def add_animal(name, species, breed, birthday, sex, castrated, weight, image_path):
    """Add a new animal to the database."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Start a transaction
            cursor.execute('BEGIN')

            # Insert the animal
            cursor.execute(
                "INSERT INTO animals (name, species, breed, birthday, sex, castrated, current_weight, image_path) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (name, species, breed, birthday, sex, castrated, weight, image_path)
            )
            animal_id = cursor.lastrowid

            # Add initial weight record
            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                "INSERT INTO weight_history (animal_id, date, weight) VALUES (?, ?, ?)",
                (animal_id, today, weight)
            )

            # Commit the transaction
            conn.commit()
            logger.info(f"Added animal {name} (ID: {animal_id}) successfully")
            return animal_id
    except sqlite3.Error as e:
        logger.error(f"Error adding animal {name}: {e}")
        return None


def get_animal(animal_id):
    """Get animal details by ID."""
    return execute_query(
        "SELECT * FROM animals WHERE id = ?",
        (animal_id,),
        fetch_mode='one'
    )


def update_animal(animal_id, name, species, breed, birthday, sex, castrated, weight, image_path):
    """Update an existing animal's information."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Start a transaction
            cursor.execute('BEGIN')

            # Get current weight
            cursor.execute("SELECT current_weight FROM animals WHERE id = ?", (animal_id,))
            result = cursor.fetchone()
            if not result:
                logger.warning(f"Animal ID {animal_id} not found for update")
                return False

            current_weight = result[0]

            # Update animal record
            cursor.execute(
                """UPDATE animals SET 
                   name = ?, species = ?, breed = ?, birthday = ?, 
                   sex = ?, castrated = ?, current_weight = ?, image_path = ?
                   WHERE id = ?""",
                (name, species, breed, birthday, sex, castrated, weight, image_path, animal_id)
            )

            # Add weight history if changed
            if weight != current_weight:
                today = datetime.now().strftime("%Y-%m-%d")
                cursor.execute(
                    "INSERT INTO weight_history (animal_id, date, weight) VALUES (?, ?, ?)",
                    (animal_id, today, weight)
                )

            # Commit the transaction
            conn.commit()
            logger.info(f"Updated animal ID {animal_id} successfully")
            return True
    except sqlite3.Error as e:
        logger.error(f"Error updating animal ID {animal_id}: {e}")
        return False


def delete_animal(animal_id):
    """Delete an animal and its related records."""
    try:
        # Get image path to delete file
        image_path = execute_query(
            "SELECT image_path FROM animals WHERE id = ?",
            (animal_id,),
            fetch_mode='one'
        )

        if not image_path:
            logger.warning(f"Animal ID {animal_id} not found for deletion")
            return False

        image_path = image_path[0]

        # Delete the animal (cascading delete will handle related records)
        success = execute_query(
            "DELETE FROM animals WHERE id = ?",
            (animal_id,)
        )

        if success and image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
                logger.info(f"Deleted image file: {image_path}")
            except OSError as e:
                logger.error(f"Error deleting image file {image_path}: {e}")

        logger.info(f"Deleted animal ID {animal_id} successfully")
        return success
    except Exception as e:
        logger.error(f"Error in delete_animal for ID {animal_id}: {e}")
        return False


def get_all_animals():
    """Get a list of all animals."""
    return execute_query(
        "SELECT id, name, species FROM animals ORDER BY name",
        fetch_mode='all'
    ) or []


def get_animals_by_species(species):
    """Get a list of animals filtered by species."""
    return execute_query(
        "SELECT id, name, breed FROM animals WHERE species = ? ORDER BY name",
        (species,),
        fetch_mode='all'
    ) or []


# Weight History Operations
def add_weight_record(animal_id, date, weight):
    """Add a new weight record for an animal."""
    success = execute_query(
        "INSERT INTO weight_history (animal_id, date, weight) VALUES (?, ?, ?)",
        (animal_id, date, weight)
    )

    if success:
        # Update current weight in animals table
        execute_query(
            "UPDATE animals SET current_weight = ? WHERE id = ?",
            (weight, animal_id)
        )
        logger.info(f"Added weight record for animal ID {animal_id}: {weight}kg on {date}")

    return bool(success)


def get_weight_history(animal_id):
    """Get weight history for an animal."""
    return execute_query(
        "SELECT date, weight FROM weight_history WHERE animal_id = ? ORDER BY date",
        (animal_id,),
        fetch_mode='all'
    ) or []


def delete_weight_record(weight_id):
    """Delete a weight record by ID."""
    success = execute_query(
        "DELETE FROM weight_history WHERE id = ?",
        (weight_id,)
    )

    if success:
        logger.info(f"Deleted weight record ID {weight_id}")

    return success


# Assessment Operations
def add_assessment(animal_id, date, scale_used, result):
    """Add a new assessment for an animal."""
    success = execute_query(
        "INSERT INTO assessments (animal_id, date, scale_used, result) VALUES (?, ?, ?, ?)",
        (animal_id, date, scale_used, result)
    )

    if success:
        logger.info(f"Added assessment for animal ID {animal_id} using scale {scale_used} on {date}")

    return success


def get_assessments(animal_id):
    """Get assessment history for an animal."""
    return execute_query(
        "SELECT id, date, scale_used, result FROM assessments WHERE animal_id = ? ORDER BY date DESC",
        (animal_id,),
        fetch_mode='all'
    ) or []


def get_all_assessments():
    """Get all assessments with animal information."""
    return execute_query(
        """
        SELECT a.id, a.date, a.scale_used, a.result, n.id, n.name, n.species
        FROM assessments a
        JOIN animals n ON a.animal_id = n.id
        ORDER BY a.date DESC
        """,
        fetch_mode='all'
    ) or []


def delete_assessment(assessment_id):
    """Delete an assessment by ID."""
    success = execute_query(
        "DELETE FROM assessments WHERE id = ?",
        (assessment_id,)
    )

    if success:
        logger.info(f"Deleted assessment ID {assessment_id}")

    return success


# Initialize database when module is imported
create_tables()