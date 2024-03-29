import os
import datetime
from flask import Flask, render_template, request, redirect, url_for, make_response

import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv()



app = Flask(__name__)

if os.getenv("FLASK_ENV", "development") == "development":
    app.debug = True  # debug mnode

print(os.getenv("MONGO_URI"))

cxn = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = cxn[os.getenv("MONGO_DBNAME")]



try:
    # verify the connection works by pinging the database
    cxn.admin.command("ping")  # The ping command is cheap and does not require auth.
    print(" *", "Connected to MongoDB!")  # if we get here, the connection worked!
except Exception as e:
    # the ping command failed, so the connection is not available.
    print(" * MongoDB connection error:", e)  # debug
    
    
    
@app.route("/", methods=['GET', 'POST'])
def home():
    """
    Route for the home page
    """
    if request.method == 'POST':
        search_query = request.form.get('search')
        price_filter = request.form.get('price_filter')
        created_date_filter = request.form.get('created_date_filter')
        edited_date_filter = request.form.get('edited_date_filter')
        return redirect(url_for('search_product', 
                                search=search_query,
                                price_filter=price_filter,
                                created_date_filter=created_date_filter,
                                edited_date_filter = edited_date_filter))
    docs = db.game_store.find({}).sort(
        "created_date", -1
    ).limit(12) 
    return render_template("index.html", docs=docs)


@app.route("/create", methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        game_name = request.form.get("name")
        game_price = int(request.form.get("price"))
        game_description = request.form.get("description")
        docs = {
                "name": game_name,
                "price": game_price,
                "description": game_description,
                "created_date": datetime.datetime.utcnow()
        }
        db.game_store.insert_one(docs)
    return render_template('create.html')
 

@app.route("/search", methods=["GET"])
def search_product():
    price_filter_mapping = {
        "": None,
        "low_high": ("price", 1),
        "high_low": ("price", -1)
    }
    date_filter_mapping = {
        "": None,
        "newest": ("created_date", 1),
        "oldest": ("created_date", -1)
    }

    search_query = request.args.get('search')
    price_filter = price_filter_mapping.get(request.args.get('price_filter'))
    created_date_filter = date_filter_mapping.get(request.args.get('created_date_filter'))
    edited_date_filter = date_filter_mapping.get(request.args.get('edited_date_filter'))

    sort_criteria = []
    if price_filter:
        sort_criteria.append(price_filter)
    if created_date_filter:
        sort_criteria.append(created_date_filter)
    if edited_date_filter:
        sort_criteria.append(edited_date_filter)

    query = {"name": {"$regex": search_query, "$options": "i"}} if search_query else {}
    docs = db.game_store.find(query)
    if sort_criteria:
        docs = docs.sort(sort_criteria)

    response = make_response(render_template("search_product.html", docs=docs))
    response.headers['Cache-Control'] = 'no-store'
    return response

@app.route("/delete", methods=["GET", "POST"])
def delete_game():
    
    if request.method == "POST":
        game_name = request.form.get("name")
        db.game_store.delete_one({"name": game_name})
        return redirect(url_for("home"))
    return render_template("delete.html")



@app.route("/edit_game/<game_id>", methods=["GET", "POST"])
def edit_game(game_id):
    """
    Route for GET and POST requests to the edit a game page.
    Displays a form to edit an existing game for sale.
    """
    if request.method == "GET":
        docs = db.game_store.find_one({"_id": ObjectId(game_id)})
        return render_template("edit.html", docs=docs)

    if request.method == "POST":
        name = request.form["name"]
        price = int(request.form["price"])
        description = request.form["description"]

        # Retrieve the existing created_date
        existing_game = db.game_store.find_one({"_id": ObjectId(game_id)})
        created_date = existing_game.get("created_date")

        # Update the document with new game data
        update_game = {
            "name": name,
            "price": price,
            "created_date": created_date,  # Use existing created_date
            "edited_date": datetime.datetime.utcnow(),  # Update edited_at timestamp
            "description": description
        }

        # Update the document in the database
        db.game_store.update_one({"_id": ObjectId(game_id)}, {"$set": update_game})

        return redirect(url_for("home"))


    
@app.route("/games", methods=['GET'])
def show_product():
    docs = db.game_store.find({})
    return render_template("game_display.html", docs=docs)


# route to handle any errors
@app.errorhandler(Exception)
def handle_error(e):
    """
    Output any errors - good for debugging.
    """
    return render_template("error.html", error=e)  # render the edit template


@app.route("/aboutus", methods=['GET'])
def aboutus():
    return render_template("aboutus.html")


if __name__ == "__main__":
    # use the PORT environment variable, or default to 5000
    FLASK_PORT = os.getenv("FLASK_PORT", "5000")

    # import logging
    # logging.basicConfig(filename='/home/ak8257/error.log',level=logging.DEBUG)
    app.run(port=FLASK_PORT)

"""
a

a
a
"""