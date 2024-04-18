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


# Creates a dict using the values of lst, but updating them with the ones in new_lst
def update_dict_values(lst, new_dic):
    final_dic = {}
    index = 0
    for header in headers:
        if header in new_dic:
            final_dic[header] = new_dic[header]
        else:
            final_dic[header] = lst[index]
        index += 1

    return final_dic


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
    except Exception as er:
        # TODO: Add logger to flask loggers
        logging.exception(f"Error adding restaurant: {er}")
        conn.close()
        return jsonify(
            {"message": "There is an error with your request, check your id"}
        ), 400


# TODO: Return the item normally and not wrapped in a list
@app.route("/restaurants/<string:id>", methods=["GET"])
def get_restaurant(id):
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM Restaurants WHERE id = ?", (id,))
    item = cursor.fetchone()
    if not item:
        return jsonify({"message": "Restaurant not found"}), 404
    return jsonify(parse_response([item], headers))


@app.route("/restaurants/<string:id>", methods=["PUT"])
def update_restaurant(id):
    info = request.get_json()
    conn = get_db()
    cursor = conn.cursor()

    # TODO: Use validation library Marshmallow
    # Check that rating hasn't changed
    if info["rating"] < 0 or info["rating"] > 4:
        return jsonify({"message": "Rating is invalid"}), 400

    # Check if the requested id is present in the DB
    entry = cursor.execute(
        "SELECT * FROM Restaurants WHERE id = :id_param", (id,)
    ).fetchone()
    if not entry:
        return jsonify({"message": "The id doesn't exist"}), 400

    # Update old values from the ones on the DB
    info_dict = update_dict_values(entry, info)
    # Added id to item in order to used named parameters
    info_dict["id_param"] = id

    if not info_dict:
        return jsonify({"message": "The values to update don't exist"}), 400

    try:
        cursor.execute(
            """UPDATE Restaurants 
            SET id = :id,
            rating = :rating,
            name = :name,
            site = :site,
            email = :email,
            phone = :phone,
            street = :street,
            city = :city,
            state = :state,
            lat = :lat,
            lng = :lng 
            WHERE id = :id_param
            """,
            info_dict,
        )
        conn.commit()
        return jsonify({"message": "The Restaurant was successfully updated"}), 200
    except Exception as er:
        # TODO: Add logger to flask loggers
        logging.exception(f"Error updating restaurant: {er}")
        conn.close()
        return jsonify({"message": "There is an error with your request "}), 400


#
#
# @app.route("/restaurants/<int:id>", methods=["DELETE"])
# def delete_restaurant(id):
#    cursor.execute("DELETE FROM restaurants WHERE id = ?", (id,))
#    conn.commit()
#    return {"message": "Item deleted successfully"}, 200


if __name__ == "__main__":
    app.run(debug=True)
