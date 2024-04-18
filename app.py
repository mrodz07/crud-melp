from flask import Flask, request, jsonify
import sqlite3
import csv

app = Flask(__name__)


if __name__ == "__main__":
    app.run(debug=True)
