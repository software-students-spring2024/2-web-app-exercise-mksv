import datetime
from flask import Flask, render_template, request, redirect, url_for
from bson.objectid import ObjectId
from dotenv import load_dotenv

app = Flask(__name__) 

# Unchecked route for the edit page (written before db implementation)
# Here I assumed when the db would be called so it could require edits later. 
@app.route("/edit_game/<game_id>", methods=["GET", "POST"])
def edit_game(game_id):
    """
    Route for GET and POST requests to the edit a game page.
    Displays a form to edit an existing game for sale.
    """
    if request.method == "GET":
        game = db.games.find_one({"_id": ObjectId(game_id)})
        return render_template("templates/edit.html", game=game)

    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])  # Convert price to float
        quantity = int(request.form["quantity"])  # Convert quantity to int

        # Update the document with new game data
        update_game = {
            "name": name,
            "price": price,
            "quantity": quantity,
            "edited_at": datetime.datetime.utcnow()  # Update edited_at timestamp
        }

        # Update the document in the database
        db.games.update_one({"_id": ObjectId(game_id)}, {"$set": update_data})

        return redirect(url_for("home"))
