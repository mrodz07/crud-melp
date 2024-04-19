# Restaurant CRUD

Managment API for the MELP company.

## What is this project?

This is a quick project to showcase my Python and engineering skills. I chose to use simple tools and a small time frame to show what I can accomplish with my current skills.

## How to run the project

In order to run this application the following needs to be done:

  1. Clone the project's repository and set it to the working directory: `https://github.com/mrodz07/crud-melp`
  2. Create a python virtual environment with: `venv`
  3. Install the required files with: `pip install -r requirements.txt`
  4. Initialize the database by entering the command: `python db_init.py`
  5. Run the program using the development server as follows: `flask run`

  * A postman collection is found on the doc branch

## Why Flask, SQLite and Geopy

- Flask is my favorite tool to build APIs, its small and reliable, perfect for a quick sketch or big project. I also enjoy using Phoenix, as elixir is my favorite functional language.
- SQLite is the easiest DB to play with, due to it being just a file.
- Geopy was needed for doing operations between coordinates

## If you had more time and this was a bigger project what would you use

As written in the code, I would recommend:
  - An ORM to manipulate the DB without having to write queries (if the project grew in complexity) 
  - A validation library such as Marshmallow
  - Automated tests with Pytest
  - Swagger for documentation
  - Design patterns to make the application more readable
