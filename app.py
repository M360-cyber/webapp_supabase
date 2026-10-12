import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure SQLite Database
db_path = os.path.join(app.instance_path, 'store.db')
os.makedirs(app.instance_path, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -----------------------------------------------------------------------------
# MODELS (MVT - Model Layer)
# -----------------------------------------------------------------------------
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default='Customer')
    orders = db.relationship('Order', backref='user', lazy=True)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

# -----------------------------------------------------------------------------
# TEMPLATE ROUTES (MVT - View / Template Layer)
# -----------------------------------------------------------------------------
@app.route('/users')
def view_users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/menu')
def view_menu():
    # Hardcoded list of menu items for display
    menu_items = [
        {"id": 1, "name": "Espresso Coffee", "price": 3.50},
        {"id": 2, "name": "Club Sandwich", "price": 7.00},
        {"id": 3, "name": "Fresh Orange Juice", "price": 4.00},
    ]
    return render_template('menu.html', items=menu_items)

@app.route('/orders')
def view_orders():
    orders = Order.query.all()
    return render_template('orders.html', orders=orders)

# -----------------------------------------------------------------------------
# REST API ENDPOINTS (For Thunder Client Testing)
# -----------------------------------------------------------------------------
@app.route('/api/users', methods=['GET', 'POST'])
def api_users():
    if request.method == 'POST':
        data = request.get_json()
        new_user = User(name=data['name'], email=data['email'], role=data.get('role', 'Customer'))
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created", "id": new_user.id}), 201
    
    users = User.query.all()
    return jsonify([{"id": u.id, "name": u.name, "email": u.email, "role": u.role} for u in users])

@app.route('/api/orders', methods=['GET', 'POST'])
def api_orders():
    if request.method == 'POST':
        data = request.get_json()
        new_order = Order(item_name=data['item_name'], price=data['price'], user_id=data['user_id'])
        db.session.add(new_order)
        db.session.commit()
        return jsonify({"message": "Order placed", "id": new_order.id}), 201

    orders = Order.query.all()
    return jsonify([{
        "id": o.id, 
        "item_name": o.item_name, 
        "price": o.price, 
        "user_id": o.user_id,
        "user_name": o.user.name
    } for o in orders])

# Seed database on startup
def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.first():
            u1 = User(name="Alice Smith", email="alice@example.com", role="Admin")
            u2 = User(name="Bob Jones", email="bob@example.com", role="Customer")
            db.session.add_all([u1, u2])
            db.session.commit()
            
            o1 = Order(item_name="Espresso Coffee", price=3.50, user_id=u1.id)
            o2 = Order(item_name="Club Sandwich", price=7.00, user_id=u2.id)
            db.session.add_all([o1, o2])
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
