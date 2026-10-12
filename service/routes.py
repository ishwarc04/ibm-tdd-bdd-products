"""REST routes for creating, reading, updating, deleting and querying products."""
from flask import abort, jsonify, request, render_template, url_for
from service import app
from service.models import Product, Category, DataValidationError
from service.common import status

@app.route("/")
def index():
    return render_template("index.html")

@app.errorhandler(DataValidationError)
def validation_error(error):
    return jsonify(error=str(error)), status.HTTP_400_BAD_REQUEST

@app.route("/products", methods=["POST"])
def create_products():
    product = Product().deserialize(request.get_json())
    product.create()
    return jsonify(product.serialize()), status.HTTP_201_CREATED, {
        "Location": url_for("get_products", product_id=product.id, _external=True)
    }

@app.route("/products/<int:product_id>", methods=["GET"])
def get_products(product_id):
    """READ: Retrieve a single product, or return 404."""
    product = Product.find(product_id)
    if product is None:
        abort(status.HTTP_404_NOT_FOUND)
    return jsonify(product.serialize()), status.HTTP_200_OK

@app.route("/products/<int:product_id>", methods=["PUT"])
def update_products(product_id):
    """UPDATE: Replace product attributes while retaining its ID."""
    product = Product.find(product_id)
    if product is None:
        abort(status.HTTP_404_NOT_FOUND)
    product.deserialize(request.get_json())
    product.update()
    return jsonify(product.serialize()), status.HTTP_200_OK

@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_products(product_id):
    """DELETE: Delete a product; repeated deletion remains idempotent."""
    product = Product.find(product_id)
    if product is not None:
        product.delete()
    return "", status.HTTP_204_NO_CONTENT

@app.route("/products", methods=["GET"])
def list_products():
    """LIST ALL, or filter by name, category and/or availability."""
    name = request.args.get("name")
    category = request.args.get("category")
    available = request.args.get("available")
    query = Product.query
    if name is not None:
        query = query.filter_by(name=name)
    if category is not None:
        try:
            query = query.filter_by(category=Category[category.upper()])
        except KeyError:
            abort(status.HTTP_400_BAD_REQUEST, "Invalid category")
    if available is not None:
        if available.lower() not in ("true", "false"):
            abort(status.HTTP_400_BAD_REQUEST, "Available must be true or false")
        query = query.filter_by(available=available.lower() == "true")
    return jsonify([product.serialize() for product in query.order_by(Product.id)]), status.HTTP_200_OK
