import sqlite3
import csv

connection = sqlite3.connect("database.db")

with open("SCHEMA.sql") as f:
    connection.executescript(f.read())

cursor = connection.cursor()


# Loads restaurant data from a CSV with the following columns:
# id,rating,name,site,email,phone,street,city,state,lat,lng
# Returns list of the data for db insertion
def parse_restaurant_data(csv_path):
    # The data to be inserted into the db
    parsed = []

    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)  # Read header data
        index = 0
        # e as in element
        for e in reader:
            # check for correct rating range
            if int(e["rating"]) < 0 or int(e["rating"]) > 4:
                raise Exception(f"Rating is not in the range on line {index}")
            parsed.append(
                [
                    e["id"],
                    e["rating"],
                    e["name"],
                    e["site"],
                    e["email"],
                    e["phone"],
                    e["street"],
                    e["city"],
                    e["state"],
                    e["lat"],
                    e["lng"],
                ]
            )
            index += 1

        return parsed


# Loads data parsed with parse_restaurant_data into the db
def load_restaurant_data(data):
    cursor.executemany(
        "INSERT INTO Restaurants VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        data,
    )
    connection.commit()


load_restaurant_data(parse_restaurant_data("restaurantes.csv"))
connection.commit()
connection.close()
