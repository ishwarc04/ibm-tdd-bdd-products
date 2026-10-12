"""Load a fresh product background before each BDD scenario."""
from behave import given
import requests

@given("the following products")
def step_load_products(context):
    from service.models import db, Product
    with context.app.app_context():
        db.session.query(Product).delete()
        db.session.commit()
    for row in context.table:
        product = {
            "name": row["name"],
            "description": row["description"],
            "price": row["price"],
            "available": row["available"].lower() == "true",
            "category": row["category"].upper(),
        }
        response = requests.post(context.base_url + "/products", json=product, timeout=10)
        assert response.status_code == 201, response.text
