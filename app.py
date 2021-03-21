from flask import Flask, jsonify, request, render_template,session
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import secrets

app = Flask(__name__)
app.secret_key = "d1aba190fe0b4542b3589f7d636fad42"
# Locating our base directory

basedir = os.path.abspath(os.path.dirname(__file__))

# Connecting the Database

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir,'db.sqlite')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#Initialize the database

db = SQLAlchemy(app)

# Initialize Marshmallow

ma = Marshmallow(app)

# Create a model

class Product(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(100),unique=True)
    description = db.Column(db.String(300))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)

    def __init__(self,name,description,price,qty):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty

class API_Tokens(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    api_token = db.Column(db.String(16))

    def __init__(self,name,email,api_token):
        self.name = name
        self.email = email
        self.api_token = api_token


# Create product schema

class ProductSchema(ma.Schema):

    # This specifies what fields to display
    class Meta:
        fields = ('id','name','description','price','qty')


############## Initialize the schema ####################

product_schema = ProductSchema() # This is for 1 product
products_schema = ProductSchema(many=True) # This is for many products


# To apply changes to database or to create a db.sqlite file we run the following commands: 
#-----Here db is the variable we have made for SQLAlchemy----
# from app import db
# db.create_all() 


################## Create a product #####################
@app.route('/product',methods=["POST"])
def add_product():
    try:
        name = request.json["name"]
        description = request.json["description"]
        price = request.json["price"]
        qty = request.json["qty"]
    except:
        name = request.form["name"]
        description = request.form["description"]
        price = request.form["price"]
        qty = request.form["qty"]

    new_product = Product(name,description,price,qty)

    # Registering the new product
    db.session.add(new_product)

    # To finally save it to the databse
    db.session.commit()

    # the product_schema.jsonify will help us get the dictionary for <Product 1>
    # [{'qty': 100, 'name': 'product 1', 'price': 277.9, 'description': 'First product', 'id': 1}]

    return product_schema.jsonify(new_product)


################# Get all the products ####################
@app.route('/product',methods=["GET"])
def get_products():
    # To find all the products available
    all_products = Product.query.all()
    
    # The query.all command will give us something like [<Product1>,<Product2>]
    # whereas the products_schema.jsonify will help us get the dictionary for each of them like 
    # [{'qty': 100, 'name': 'product 1', 'price': 277.9, 'description': 'First product', 'id': 1}, {'qty': 10, 'name': 'product 2', 'price': 877.9, 'description': 'Second product', 'id': 2}]
    
    return products_schema.jsonify(all_products)


################# Get a single product ####################

@app.route('/product/<id>',methods=["GET"])
def get_product(id):

    # To find the product with given id
    product = Product.query.get(id)

    return product_schema.jsonify(product)


################### Update a product #######################
@app.route('/product/<id>',methods=["PUT"])
def update_product(id):
    product = Product.query.get(id)
    product.name = request.json["name"]
    product.description = request.json["description"]
    product.price = request.json["price"]
    product.qty = request.json["qty"]

    # Save it to the databse
    db.session.commit()

    # the product_schema.jsonify will help us get the dictionary for <Product 1>
    # [{'qty': 100, 'name': 'product 1', 'price': 277.9, 'description': 'First product', 'id': 1}]

    return product_schema.jsonify(product)


#################### Delete a Product ######################

@app.route('/product/<id>',methods=["DELETE"])
def delete_product(id):

    # To find the product with given id
    product = Product.query.get(id)

    # delete the product
    db.session.delete(product)

    # Commit the change
    db.session.commit()

    return product_schema.jsonify(product)


@app.route('/')
def home():
    return render_template("home.html")

@app.route('/events')
def events():
    if session.get("api_key"):
        return render_template("events.html",api_key = session["api_key"])
    return render_template("events.html",api_key = "")

@app.route("/generate_api",methods=["POST","GET"])
def generate_api():
    if request.method == "POST":
        name = request.form['name']
        emailx = request.form['email']

        check_exists = API_Tokens.query.filter_by(name=name,email = emailx).first()

        if check_exists != [] and check_exists != None:
            session["api_key"] = check_exists.api_token
            return jsonify({"status":"500","api_token":check_exists.api_token})

        token = secrets.token_hex(8)

        x = API_Tokens(name,emailx,token)

        db.session.add(x)

        db.session.commit()

        session["api_key"] = token

        return jsonify({"status":"200","api_token":token})
    api_key_token = request.args.get("api_key")
    quer = API_Tokens.query.filter_by(api_token=api_key_token).first()

    return jsonify({"status":"OK"}) if quer else jsonify({"status":"NOT OK"})


# Run the Server
if __name__ == "__main__":
    app.run(debug=True)