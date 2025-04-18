from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import init_db, register_user, login_user, add_product_to_tracking, get_all_user_products, get_all_product_entries
from scraper import scrape_data

app = Flask(__name__)
init_db()

#For registering the user; requires email, password and username in form data
#returns confirmation of registration and user id
@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    username = request.form.get('username')

    if not all([email, password, username]):
        return jsonify({"error": "All fields are required"}), 400

    hashed_password = generate_password_hash(password)

    return register_user(email=email, hashed_password=hashed_password, username=username)



# FOr logging in the user to track their items, requires email and password
# returns user id and username
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    if not all([email, password]):
        return jsonify({"error": "Email and password required"}), 400
    user = login_user(email=email)

    if user and check_password_hash(user[2], password):
        return jsonify({"id": user[0], "username": user[1]})
    else:
        return jsonify({"error": "Invalid email or password"}), 401
    
#Scrapes a url for the product name and price; only works for daraz atm
# takes in a url, user_id and percentage for which the price should reduce to recieve an email;
# returns a name and price   
@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form.get('url')
    user_id = request.form.get('user_id')
    percentage = request.form.get('percentage')
    if not url:
        return jsonify({"error": "URL is required"}), 400
    if not percentage:
        percentage = 10
    
    name, price = scrape_data(url=url)
    id = add_product_to_tracking(product_name=name, product_price=price, percentage=percentage, product_url=url, user_id=user_id)
    if id == "":
        return jsonify({"Not Found": "Error adding to database"}), 401
        
    if name == "":
        return jsonify({"Not Found": "Unable to find the product"}), 401
    else:
        return jsonify({"Status":"Product is being tracked","Name": name, "Current_price": price})
    
#gets all the products that is being tracked for a user
#Takes a user_id in the params and returns a list of products       
@app.route('/get_user_products', methods=['GET'])
def get_user_products():
    user_id = request.args.get('user_id')  # Changed to 'request.args.get' for GET requests, use query params
    products = get_all_user_products(user_id=user_id)  # Fetch all products for the user
    
    if products == []:
        return jsonify({"Not Found": "Unable to fetch products for this user"}), 404

    # Create a dictionary to store product_id as key and a nested dictionary as value
    product_data = {}
    for product in products:
        product_data[product[1]] = {  # product[0] is product_id
            "Name": product[0],  # product[1] is product_name
            "Price": product[2]  # product[2] is product_price
        }

    return jsonify(product_data)

@app.route('/get_product_data', methods=['GET'])
def get_product_data():
    product_id = request.args.get('product_id')  # Changed to 'request.args.get' for GET requests, use query params
    entries = get_all_product_entries(product_id=product_id)  # Fetch all products for the user
    
    if entries == []:
        return jsonify({"Not Found": "Unable to fetch entries for this product"}), 404

    # Create a dictionary to store product_id as key and a nested dictionary as value
    product_data = {}
    for product in entries:
        product_data[product[0]] = {  # product[0] is timestamp
            "Name": product[1],  # product[1] is product_name
            "Price": product[2]  # product[2] is product_price
        }

    return jsonify(product_data)

if __name__ == '__main__':
    app.run(debug=True)
    
    

        
