"""
database.py - Database operations for CineBook
Using Python's built-in sqlite3 library.
"""

import sqlite3

DB_NAME = "cinebook.db"

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Creates tables and populates sample data if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    )
    """)

    # 2. Movies table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        genre TEXT NOT NULL,
        language TEXT NOT NULL,
        duration TEXT NOT NULL,
        rating REAL NOT NULL,
        release_date TEXT NOT NULL,
        description TEXT NOT NULL,
        director TEXT NOT NULL,
        cast TEXT NOT NULL,
        poster TEXT NOT NULL
    )
    """)

    # 3. Theatres table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS theatres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        facilities TEXT NOT NULL
    )
    """)

    # 4. Shows table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shows (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id INTEGER NOT NULL,
        theatre_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (movie_id) REFERENCES movies (id),
        FOREIGN KEY (theatre_id) REFERENCES theatres (id)
    )
    """)

    # 5. Bookings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        movie TEXT NOT NULL,
        theatre TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        seats TEXT NOT NULL,
        amount REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'CONFIRMED'
    )
    """)

    conn.commit()

    cursor.execute("SELECT COUNT(*) as count FROM movies")
    count = cursor.fetchone()["count"]

    if count == 0:
        seed_sample_data(conn)

    conn.close()

def seed_sample_data(conn):
    """Inserts initial demo data with official posters."""
    cursor = conn.cursor()

    users_data = [
        ("Demo User", "demo@cinebook.com", "9876543210", "Demo123", "user"),
        ("Admin", "admin@cinebook.com", "9999999999", "admin123", "admin")
    ]
    cursor.executemany("""
    INSERT INTO users (name, email, phone, password, role)
    VALUES (?, ?, ?, ?, ?)
    """, users_data)

    movies_data = [
        (
            "Interstellar", "Sci-Fi", "English", "169 min", 8.7, "2024-11-05",
            "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
            "Christopher Nolan", "Matthew McConaughey, Anne Hathaway, Jessica Chastain",
            r"C:\\Users\\Roshan Sharma\\.vscode\\CINEBOOK\\posters\\interstellar.jpg"
        ),
        (
            "The Dark Knight", "Action", "English", "152 min", 9.0, "2024-07-18",
            "When the menace known as the Joker wreaks havoc on Gotham, Batman faces his greatest psychological test.",
            "Christopher Nolan", "Christian Bale, Heath Ledger, Aaron Eckhart",
            r"C:\\Users\\Roshan Sharma\\.vscode\\CINEBOOK\\posters\\the dark knight.jpg"
        ),
        (
            "Inception", "Sci-Fi", "English", "148 min", 8.8, "2024-08-10",
            "A thief who steals corporate secrets through dream-sharing is tasked with planting an idea into the mind of a C.E.O.",
            "Christopher Nolan", "Leonardo DiCaprio, Joseph Gordon-Levitt, Elliot Page",
            r"C:\\Users\\Roshan Sharma\\.vscode\\CINEBOOK\\posters\\inception.jpg"
        ),
        (
            "The Grand Budapest Hotel", "Comedy", "English", "99 min", 8.1, "2024-03-28",
            "A writer encounters the owner of an aging hotel recounting his adventures as a lobby boy.",
            "Wes Anderson", "Ralph Fiennes, F. Murray Abraham, Mathieu Amalric",
            r"C:\\Users\\Roshan Sharma\\.vscode\\CINEBOOK\\posters\\the grand budapest hotel.jpg"
        ),
        (
            "La La Land", "Romance", "English", "128 min", 8.0, "2024-12-25",
            "While navigating their careers in Los Angeles, a pianist and an actress fall in love.",
            "Damien Chazelle", "Ryan Gosling, Emma Stone, Rosemarie DeWitt",
            r"C:\\Users\\Roshan Sharma\\.vscode\\CINEBOOK\\posters\\la la land.jpg"
        ),
        (
            "Avengers: Endgame", "Action", "English", "181 min", 8.4, "2024-04-26",
            "After Infinity War, the universe is in ruins. The Avengers assemble once more to reverse Thanos' actions.",
            "Anthony Russo, Joe Russo", "Robert Downey Jr., Chris Evans, Mark Ruffalo",
            r"C:\\Users\\Roshan Sharma\\.vscode\\CINEBOOK\\posters\\avengers endgame.jpg"
        ),
        (
            "Spirited Away", "Animation", "Japanese", "125 min", 8.6, "2024-07-20",
            "During her family's move to the suburbs, a 10-year-old girl wanders into a world of spirits.",
            "Hayao Miyazaki", "Rumi Hiiragi, Miyu Irino, Mari Natsuki",
            r"C:\\Users\\Roshan Sharma\\.vscode\\CINEBOOK\\posters\\spirited away.jpg"
        )
    ]
    cursor.executemany("""
    INSERT INTO movies (title, genre, language, duration, rating, release_date, description, director, cast, poster)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, movies_data)

    theatres_data = [
        ("CineBook Central", "Connaught Place, Central City", "Dolby Atmos, 4K Laser, Recliner Seats, Cafeteria"),
        ("CineBook Mall", "Phoenix Market Mall, Sector 18", "IMAX Screen, Gourmet Food Court, Parking"),
        ("CineBook Downtown", "Main Boulevard, Downtown", "7.1 Surround Sound, Valet Parking, Wheelchair Accessible"),
        ("CineBook City Centre", "Metro Junction Mall, West Wing", "Dolby Digital, Express Concessions, 3D Enabled")
    ]
    cursor.executemany("""
    INSERT INTO theatres (name, location, facilities)
    VALUES (?, ?, ?)
    """, theatres_data)

    sample_bookings = [
        (
            "CB20260001", "Demo User", "demo@cinebook.com", "9876543210",
            "Interstellar", "CineBook Central", "Today", "07:00 PM",
            "A1, B4", 330.0, "CONFIRMED"
        ),
        (
            "CB20260002", "Rahul Sharma", "rahul@example.com", "9811223344",
            "The Dark Knight", "CineBook Mall", "Today", "04:00 PM",
            "C3, D6", 380.0, "CONFIRMED"
        )
    ]
    cursor.executemany("""
    INSERT INTO bookings (booking_id, name, email, phone, movie, theatre, date, time, seats, amount, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_bookings)

    conn.commit()

def get_all_movies(search_query="", genre_filter="All", lang_filter="All"):
    """Fetches movies with optional filtering."""
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM movies WHERE 1=1"
    params = []

    if search_query:
        query += " AND (title LIKE ? OR cast LIKE ? OR director LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"])

    if genre_filter != "All":
        query += " AND genre = ?"
        params.append(genre_filter)

    if lang_filter != "All":
        query += " AND language = ?"
        params.append(lang_filter)

    cursor.execute(query, params)
    movies = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return movies

def get_all_theatres():
    """Fetches all theatre records."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM theatres")
    theatres = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return theatres

def get_occupied_seats(movie_title, theatre_name, date_str, time_str):
    """Finds which seats are already occupied for a specific show."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT seats FROM bookings
    WHERE movie = ? AND theatre = ? AND date = ? AND time = ? AND status = 'CONFIRMED'
    """, (movie_title, theatre_name, date_str, time_str))

    rows = cursor.fetchall()
    occupied = set()
    for row in rows:
        seat_list = [s.strip() for s in row["seats"].split(",") if s.strip()]
        occupied.update(seat_list)

    conn.close()
    return occupied

def save_booking(booking_id, name, email, phone, movie, theatre, date, time, seats_list, amount):
    """Saves a new confirmed booking."""
    conn = get_connection()
    cursor = conn.cursor()
    seats_str = ", ".join(seats_list)
    cursor.execute("""
    INSERT INTO bookings (booking_id, name, email, phone, movie, theatre, date, time, seats, amount, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'CONFIRMED')
    """, (booking_id, name, email, phone, movie, theatre, date, time, seats_str, amount))
    conn.commit()
    conn.close()
    return True

def get_bookings_by_email(email):
    """Fetches bookings for a user email."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings WHERE email = ? ORDER BY id DESC", (email,))
    bookings = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return bookings

def get_all_bookings():
    """Fetches all bookings in the system for admin view."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings ORDER BY id DESC")
    bookings = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return bookings

def cancel_booking_by_id(booking_id):
    """Updates the status of a booking to CANCELLED."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE bookings SET status = 'CANCELLED' WHERE booking_id = ?", (booking_id,))
    conn.commit()
    conn.close()
    return True

def get_admin_metrics():
    """Returns dashboard counts for admin overview."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM movies")
    movies_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM theatres")
    theatres_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM users")
    users_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as revenue FROM bookings WHERE status = 'CONFIRMED'")
    row = cursor.fetchone()

    conn.close()
    return {
        "movies": movies_count,
        "theatres": theatres_count,
        "users": users_count,
        "bookings": row["count"],
        "revenue": row["revenue"]
    }

def add_new_movie(title, genre, language, duration, rating, release_date, description, director, cast, poster):
    """Adds a new movie to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO movies (title, genre, language, duration, rating, release_date, description, director, cast, poster)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, genre, language, duration, rating, release_date, description, director, cast, poster))
    conn.commit()
    conn.close()

def get_all_users():
    """Retrieves all registered users for admin display."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, phone, role FROM users")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users


