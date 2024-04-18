from flask import Flask, request, jsonify, g
import sqlite3
import json
import logging
import geopy.distance
import statistics

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

    if not item:
        return jsonify({"message": "Can't register empty value"}), 400

    # Check that provided values are enough for all columns
    if len(set(item)) != len(set(headers)):
        return jsonify({"message": "There are values missing on your request"}), 400

    if item["rating"] < 0 or item["rating"] > 4:
        return jsonify({"message": "Invalid rating"}), 400

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

    if not info:
        return jsonify({"message": "Can't update empty values"}), 400

    # TODO: Use validation library Marshmallow
    # Check that rating isn't invalid
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


@app.route("/restaurants/<string:id>", methods=["DELETE"])
def delete_restaurant(id):
    conn = get_db()
    cursor = conn.cursor()

    # TODO: Return clean DB response
    # Check if the requested id is present in the DB
    entry = cursor.execute("SELECT * FROM Restaurants WHERE id = ?", (id,)).fetchone()
    if not entry:
        return jsonify({"message": "The id doesn't exist"}), 400

    try:
        cursor.execute("DELETE FROM Restaurants WHERE id = ?", (id,))
        conn.commit()
    except Exception as er:
        # TODO: Add logger to flask loggers
        logging.exception(f"Error deleting restaurant: {er}")
        conn.close()
        return jsonify({"message": "There was an error when deleting your value"}), 400

    return {"message": "Item deleted successfully"}, 200


# Returns statistics about the relation between the provided point and the restaurants int the DB
# Expects three query params: latitude, longitude and radius
@app.route("/restaurants/statistics", methods=["GET"])
def get_statistics():
    args = request.args
    data = []
    lat = args.get("latitude", default=0, type=float)
    lon = args.get("longitude", default=0, type=float)
    rad = args.get("radius", default=0, type=int)
    main_coords = (lat, lon)
    matching_points = []
    matching_ratings = []

    total_point_count = 0
    total_rate_avg = 0
    total_rate_std = 0

    # TODO: Check for correct latitude, longitude

    if lat == 0 or lon == 0 or rad == 0:
        return jsonify({"message": "Empty values were supplied"}), 400

    cursor = get_db().cursor()

    try:
        data = cursor.execute("SELECT id, lat, lng, rating FROM Restaurants").fetchall()
    except Exception as er:
        # TODO: Add logger to flask loggers
        logging.exception(f"Error quering restaurant coordinates: {er}")

    # Remember that the indices mean:
    # 0: id
    # 1: lat
    # 2: lng
    # 3: rating
    for row in data:
        current_coords = (row[1], row[2])
        if geopy.distance.geodesic(main_coords, current_coords).m <= rad:
            matching_points.append(row)
            total_rate_avg += row[3]
            matching_ratings.append(row[3])

    total_rate_std = statistics.stdev(matching_ratings)
    total_point_count = len(matching_points)
    total_rate_avg = total_rate_avg / len(matching_points)

    return jsonify(
        {"count": total_point_count, "avg": total_rate_avg, "std": total_rate_std}
    )


if __name__ == "__main__":
    app.run(debug=True)
