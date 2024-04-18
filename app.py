from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Connect to local database
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Create the database
# Rating must be between 1 and 4. Checking through the app, constraint may be useful
cursor.execute(
    """CREATE TABLE IF NOT EXISTS Restaurants (id TEXT PRIMARY KEY, rating INTEGER, name TEXT, site TEXT, email TEXT, phone, TEXT, street TEXT, city TEXT, state TEXT, lat FLOAT, lng FLOAT)"""
)
conn.commit()

if __name__ == "__main__":
    app.run(debug=True)
