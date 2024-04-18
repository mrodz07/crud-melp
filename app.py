from flask import Flask, request, jsonify, g
import sqlite3
import json
import logging
import csv

app = Flask(__name__)

DATABASE = "database.db"

# TODO: Get headers from query with cursor.description
headers = [
    "id",
    "rating",
    "name",
    "site",
    "email",
    "phone",
    "street",
    "city",
    "state",
    "lat",
    "lng",
]


# Saves the db connection for further use
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


# Parses list data to a dict to be used in jsonify
def parse_response(lst, headers):
    parsed = []
    for item in lst:
        new_item = {}
        # Enumerate gives the index and value of the headers array
        for i in enumerate(headers):
            new_item[i[1]] = item[i[0]]
        parsed.append(new_item)

    if len(parsed) > 1:
        return json.dumps(parsed)
    if len(parsed) == 1:
        return json.dumps(parsed[0])
    else:
        return json.dumps({})


@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM Restaurants")
    return jsonify(parse_response(cursor.fetchall(), headers))


@app.route("/restaurants", methods=["POST"])
def add_restaurant():
    conn = get_db()
    cursor = conn.cursor()
    item = request.get_json()
    try:
        cursor.execute(
            "INSERT INTO Restaurants VALUES (:id, :rating, :name, :site, :email, :phone, :street, :city, :state, :lat, :lng)",
            item,
        )
        conn.commit()
        return jsonify({"message": "Restaurant added successfully"}), 201
    except sqlite3.IntegrityError as er:
        logging.exception(f"Error adding restaurant: {er}")
        conn.close()
        return jsonify({"message": "The restaurant id is already registered"}), 400


# TODO: Return the item normally and not wrapped in a list
@app.route("/restaurants/<string:id>", methods=["GET"])
def get_restaurant(id):
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM Restaurants WHERE id = ?", (id,))
    item = cursor.fetchone()
    if not item:
        return jsonify({"message": "Restaurant not found"}), 404
    return jsonify(parse_response([item], headers))


# @app.route("/restaurants/<int:id>", methods=["PUT"])
# def update_restaurant(id):
#    item = request.get_json()
#    cursor.execute("UPDATE restaurants SET name = ? WHERE id = ?", (item["name"], id))
#    conn.commit()
#    return {"message": "Item updated successfully"}, 200
#
#
# @app.route("/restaurants/<int:id>", methods=["DELETE"])
# def delete_restaurant(id):
#    cursor.execute("DELETE FROM restaurants WHERE id = ?", (id,))
#    conn.commit()
#    return {"message": "Item deleted successfully"}, 200


if __name__ == "__main__":
    app.run(debug=True)
