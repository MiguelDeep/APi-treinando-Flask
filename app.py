#importing
from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin,login_user, LoginManager,login_required,logout_user,current_user

app = Flask(__name__)
app.config['SECRET_KEY'] ='minha_chave_123'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///ecommerce.db'

login_manager = LoginManager()
db = SQLAlchemy(app)

#Authenticating my application
login_manager.init_app(app)
login_manager.login_view = 'login'

#
CORS(app)

#Modeling
#Use(id ,username ,password)
class User(db.Model, UserMixin):
  id = id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), nullable=False ,unique=True)
  password = db.Column(db.String(10),nullable=False)
  card = db.relationship('CardItem', backref='user',lazy=True)
#Product(id, name,price ,description)

class Product(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120), nullable=False)
  price = db.Column(db.Float, nullable=False)
  description = db.Column(db.Text)

class CardItem(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
  product_id = db.Column(db.Integer, db.ForeignKey('product.id'),nullable=False)

#Create a Route of Favorites  
class ItemFavority(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
  product_id = db.Column(db.Integer, db.ForeignKey('product.id'),nullable=False)
  
  
  

#Login
@login_manager.user_loader
def login(user_id):
    return User.query.get(int(user_id))
@app.route('/login',methods=['POST'])
def login():
  data = request.json
  user = User.query.filter_by(username=data.get("username")).first()
  if user and data.get('password') == user.password:

      login_user(user)
      return jsonify({"message":"Logged successfully!"}),200 
  
  return jsonify({"message":"Unauthorized. Invalid credentials"}),401 
  
  
#Logout user
@app.route('/logout',methods=['POST'])
@login_required
def logout():
  logout_user()
  return jsonify({"message":"Logout successfully!"}),200

    
#Route to add product.
@app.route('/api/product/add',methods=['POST'])
@login_required
def add_product():
  data = request.json
  if 'name' in data and 'price' in data:
  #That way if he does not find it will assign the value of the second parameter.
      product = Product(name=data.get("name","null"),price=data.get("price"),description=data.get("description","null"))
      db.session.add(product)
      db.session.commit()
      return jsonify({"message":"Product added successfully!"}),200
  return jsonify({"message":"Error when registering product."}),400    



# Delete route products
@app.route("/api/products/delete/<int:product_id>",methods=["DELETE"])
@login_required
def delete_products(product_id):
  #Recover the product from our database.
  #Check if it exists.
  #If it exists, delete from the database. 
  #If it does not exist, return 404.
  product = Product.query.get(product_id) 
  if product:
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message":"Product deleted successfully"}),200
  return jsonify({"message":"Product not found."}),404 



# Taking the product by ID
@app.route("/api/products/<int:product_id>",methods=["GET"])
def get_product(product_id):
  #When bringing products we do not need to use session or commit, because we are not changing any information.
    product = Product.query.get(product_id) 
    if product:
      return jsonify({
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "description": product.description
        }),200
    return jsonify({"message":"Product not found."}),404 


# Updating products
@app.route("/api/products/update/<int:product_id>",methods=["PUT"])
@login_required
def update_products(product_id):
  #Recover the product from our database.
  #Check if it exists.
  #If it exists, update from the database. 
  #If it does not exist, return 404.
  product = Product.query.get(product_id) 
  if not product:
     return jsonify({"message":"Product not found."}),404 
  
  data = request.json
  if 'name' in data: 
    product.name = data["name"]
  if 'price' in data:
    product.price = data["price"]
  if 'description' in data:
    product.description = data["description"]
  db.session.commit()
  return jsonify({"message:":"Successfully updated."})


#List Products
@app.route("/api/products",methods=["GET"])
def get_products():
  #When bringing products we do not need to use session or commit, because we are not changing any information.
  product = Product.query.all()
  product_list = []
  for products in product:
      product_data = {
        "id": products.id,
        "name": products.name,
        "price": products.price,
      }
      product_list.append(product_data)
      
  return jsonify(product_list) 



#Checkout
@app.route('/api/cart/add/<int:product_id>',methods=["POST"])
@login_required
def cart_add_product(product_id):
  #user
  user = User.query.get(int(current_user.id))
  #Product
  product = Product.query.get(product_id)
  if user and product:
    cart = CardItem(user_id=user.id,product_id=product.id)
    db.session.add(cart)
    db.session.commit()
    return jsonify({"message":"Item added to the cart successfully"}),200
  return jsonify({"message":"Failed to add item to the cart."}),400


#remove item from cart
@app.route("/api/cart/remove/<int:item_id>",methods=["DELETE"])
@login_required
def delete_item(item_id):
 cart_item = CardItem.query.filter_by(user_id=current_user.id,product_id=item_id).first()
 if cart_item:
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({"message":"Item removed from the cart successfully."}),200
 return jsonify({"message":"Failed to remove item from the cart."}),400 

#returns the carts
@app.route("/api/cart",methods=["GET"])
@login_required
def get_cart():
  user = User.query.get(int(current_user.id))
  cart = CardItem.query.all()
  cart_list = []
  for carts in cart:
      product = Product.query.get(int(carts.product_id))
      cart_data = {
        "id": carts.id,
        "user_id": carts.user_id,
        "product_name": product.name,
        "product_price": product.price,
        "product_description": product.description,
      }
      cart_list.append(cart_data)
      
  return jsonify(cart_list) 

#Rota de checkout
@app.route('/api/cart/checkout', methods=['POST'])
@login_required
def checkout():
  user = User.query.get(int(current_user.id))
  cart_item = user.card
  for items in cart_item:
    db.session.delete(items)
  db.session.commit()
  return jsonify({"message":"Checkout successful. Cart has been cleared."})

#defining a root route for application.
@app.route('/')
def hello_world():
  return 'Hello World'



if __name__ == "__main__":
  app.run(debug=True)
  
  #35minu
