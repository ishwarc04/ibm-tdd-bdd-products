import os
os.environ["DATABASE_URI"] = "sqlite:///:memory:"
import unittest
from service import app
from service.models import db, Product, Category, DataValidationError
from tests.factories import ProductFactory
from service.common import status
BASE_URL = "/products"

class TestProductRoutes(unittest.TestCase):
    def setUp(self):
        self.context = app.app_context()
        self.context.push()
        app.config["TESTING"] = True
        db.create_all()
        db.session.query(Product).delete()
        db.session.commit()
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_get_product(self):
        """It should Read a single Product"""
        product = ProductFactory()
        resp = self.client.post(
            BASE_URL,
            json=product.serialize(),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        new_product = resp.get_json()
        product_id = new_product["id"]

        resp = self.client.get(f"{BASE_URL}/{product_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(data["id"], product_id)
        self.assertEqual(data["name"], product.name)

    def test_update_product(self):
        """It should Update an existing Product"""
        product = ProductFactory()
        resp = self.client.post(
            BASE_URL,
            json=product.serialize(),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        new_product = resp.get_json()
        product_id = new_product["id"]

        new_product["description"] = "unknown"

        resp = self.client.put(
            f"{BASE_URL}/{product_id}",
            json=new_product,
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        updated_product = resp.get_json()
        self.assertEqual(
            updated_product["description"],
            "unknown"
        )
        self.assertEqual(updated_product["id"], product_id)

    def test_delete_product(self):
        """It should Delete a Product"""
        products = ProductFactory.create_batch(5)
        for product in products:
            resp = self.client.post(
                BASE_URL,
                json=product.serialize(),
                content_type="application/json"
            )
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED
            )

        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        original_count = len(resp.get_json())

        product_id = resp.get_json()[0]["id"]

        resp = self.client.delete(
            f"{BASE_URL}/{product_id}"
        )
        self.assertEqual(
            resp.status_code,
            status.HTTP_204_NO_CONTENT
        )
        self.assertEqual(resp.data, b"")

        resp = self.client.get(
            f"{BASE_URL}/{product_id}"
        )
        self.assertEqual(
            resp.status_code,
            status.HTTP_404_NOT_FOUND
        )

        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(resp.get_json()),
            original_count - 1
        )

    def test_get_product_list(self):
        """It should Get a list of Products"""
        for product in ProductFactory.create_batch(5):
            resp = self.client.post(
                BASE_URL,
                json=product.serialize(),
                content_type="application/json"
            )
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED
            )

        resp = self.client.get(BASE_URL)
        self.assertEqual(
            resp.status_code,
            status.HTTP_200_OK
        )

        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_query_product_list_by_name(self):
        """It should Query Products by Name"""
        products = ProductFactory.create_batch(5)
        products[0].name = "Hat"

        for product in products:
            resp = self.client.post(
                BASE_URL,
                json=product.serialize(),
                content_type="application/json"
            )
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED
            )

        resp = self.client.get(
            BASE_URL,
            query_string={"name": "Hat"}
        )
        self.assertEqual(
            resp.status_code,
            status.HTTP_200_OK
        )

        data = resp.get_json()
        self.assertGreater(len(data), 0)

        for product in data:
            self.assertEqual(product["name"], "Hat")

    def test_query_product_list_by_category(self):
        """It should Query Products by Category"""
        products = ProductFactory.create_batch(5)

        for product in products:
            product.category = Category.FOOD
            resp = self.client.post(
                BASE_URL,
                json=product.serialize(),
                content_type="application/json"
            )
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED
            )

        resp = self.client.get(
            BASE_URL,
            query_string={"category": Category.FOOD.name}
        )
        self.assertEqual(
            resp.status_code,
            status.HTTP_200_OK
        )

        data = resp.get_json()
        self.assertEqual(len(data), 5)

        for product in data:
            self.assertEqual(
                product["category"],
                Category.FOOD.name
            )

    def test_query_product_list_by_availability(self):
        """It should Query Products by Availability"""
        products = ProductFactory.create_batch(10)

        for index, product in enumerate(products):
            product.available = index < 5
            resp = self.client.post(
                BASE_URL,
                json=product.serialize(),
                content_type="application/json"
            )
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED
            )

        resp = self.client.get(
            BASE_URL,
            query_string={"available": "true"}
        )
        self.assertEqual(
            resp.status_code,
            status.HTTP_200_OK
        )

        data = resp.get_json()
        self.assertEqual(len(data), 5)

        for product in data:
            self.assertTrue(product["available"])

    def test_filters_exclude_nonmatching_products(self):
        """Filters include every match and exclude unrelated products."""
        specs = [("Hat", Category.CLOTHS, True),
                 ("Hat", Category.CLOTHS, False),
                 ("Apple", Category.FOOD, True)]
        for name, category, available in specs:
            product = ProductFactory(name=name, category=category, available=available)
            self.assertEqual(self.client.post(BASE_URL, json=product.serialize()).status_code, 201)
        for query, expected in [({"name": "Hat"}, 2),
                                ({"category": "CLOTHS"}, 2),
                                ({"available": "false"}, 1),
                                ({"name": "Hat", "available": "true"}, 1),
                                ({"name": "Missing"}, 0)]:
            with self.subTest(query=query):
                response = self.client.get(BASE_URL, query_string=query)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.get_json()), expected)

    def test_missing_product_and_idempotent_delete(self):
        self.assertEqual(self.client.get(BASE_URL + "/999").status_code, 404)
        self.assertEqual(self.client.put(BASE_URL + "/999", json={}).status_code, 404)
        self.assertEqual(self.client.delete(BASE_URL + "/999").status_code, 204)

    def test_invalid_filter(self):
        for query in ({"category": "INVALID"}, {"available": "maybe"}):
            self.assertEqual(self.client.get(BASE_URL, query_string=query).status_code, 400)

    def test_invalid_product_input(self):
        valid = ProductFactory().serialize()
        for changes in ({"name": ""}, {"available": "false"}, {"price": "NaN"},
                        {"price": "-1"}, {"category": "INVALID"}):
            with self.subTest(changes=changes):
                self.assertEqual(self.client.post(BASE_URL, json=valid | changes).status_code, 400)
        self.assertEqual(self.client.post(BASE_URL, json={}).status_code, 400)
        self.assertEqual(self.client.post(BASE_URL, json=[]).status_code, 400)
        self.assertEqual(self.client.post(BASE_URL, data="plain text").status_code, 415)
        self.assertEqual(Product.all(), [])

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'id="search-btn"', response.data)
