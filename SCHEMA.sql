DROP TABLE IF EXISTS Restaurants;

CREATE TABLE Restaurants (
    id TEXT PRIMARY KEY,
    rating INTEGER NOT NULL,
    name TEXT NOT NULL,
    site TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    street TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    lat FLOAT NOT NULL,
    lng FLOAT NOT NULL
);
