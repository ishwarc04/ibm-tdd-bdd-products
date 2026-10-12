import os
os.environ["DATABASE_URI"] = "sqlite:///:memory:"
import unittest
from service import app
from service.models import db, Product, Category, DataValidationError
from tests.factories import ProductFactory
from service.common import status
BASE_URL = "/products"

class TestProductModel(unittest.TestCase):
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

    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        product.create()
        self.assertIsNotNone(product.id)

        found_product = Product.find(product.id)
        self.assertIsNotNone(found_product)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(
            found_product.description,
            product.description
        )
        self.assertEqual(found_product.price, product.price)

    def test_update_a_product(self):
        """It should Update a Product"""
        product = ProductFactory()
        product.create()
        self.assertIsNotNone(product.id)

        original_id = product.id
        product.name = "Updated Product"
        product.description = "testing"
        product.update()

        self.assertEqual(product.id, original_id)
        self.assertEqual(product.name, "Updated Product")
        self.assertEqual(product.description, "testing")

        found_product = Product.find(original_id)
        self.assertIsNotNone(found_product)
        self.assertEqual(found_product.id, original_id)
        self.assertEqual(found_product.name, "Updated Product")
        self.assertEqual(found_product.description, "testing")

    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        product.create()
        self.assertIsNotNone(product.id)

        self.assertEqual(len(Product.all()), 1)

        product.delete()

        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should List all Products, starting from an empty database."""
        self.assertEqual(Product.all(), [])
        products = ProductFactory.create_batch(2)
        for product in products:
            product.create()
        found = Product.all()
        self.assertEqual(len(found), 2)
        self.assertCountEqual([p.id for p in found], [p.id for p in products])
        self.assertCountEqual([p.serialize() for p in found], [p.serialize() for p in products])

    def test_find_by_name(self):
        """It should Find a Product by Name"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()

        name = products[0].name
        count = len([
            product for product in products
            if product.name == name
        ])

        found = Product.find_by_name(name)

        self.assertEqual(len(found), count)
        for product in found:
            self.assertEqual(product.name, name)

    def test_find_by_category(self):
        """It should Find Products by Category"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        category = products[0].category
        count = len([
            product for product in products
            if product.category == category
        ])

        found = Product.find_by_category(category)

        self.assertEqual(len(found), count)
        for product in found:
            self.assertEqual(product.category, category)

    def test_find_by_availability(self):
        """It should Find Products by Availability"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        available = products[0].available
        count = len([
            product for product in products
            if product.available == available
        ])

        found = Product.find_by_availability(available)

        self.assertEqual(len(found), count)
        for product in found:
            self.assertEqual(product.available, available)

    def test_update_without_id(self):
        product = ProductFactory(id=None)
        with self.assertRaises(DataValidationError):
            product.update()

    def test_queries_exclude_nonmatches(self):
        first = ProductFactory(name="Hat", category=Category.CLOTHS, available=True)
        second = ProductFactory(name="Apple", category=Category.FOOD, available=False)
        first.create()
        second.create()
        self.assertEqual([p.id for p in Product.find_by_name("Hat")], [first.id])
        self.assertEqual([p.id for p in Product.find_by_category(Category.FOOD)], [second.id])
        self.assertEqual([p.id for p in Product.find_by_availability(False)], [second.id])
        self.assertEqual(Product.find_by_name("Missing"), [])
