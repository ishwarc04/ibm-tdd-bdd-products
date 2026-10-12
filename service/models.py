"""Persistent product model and query operations."""
from decimal import Decimal, InvalidOperation
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Category(Enum):
    UNKNOWN = 0
    CLOTHS = 1
    FOOD = 2
    HOUSEWARES = 3
    AUTOMOTIVE = 4
    TOOLS = 5

class DataValidationError(ValueError):
    """Invalid product input."""

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(1024), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    available = db.Column(db.Boolean, nullable=False, default=True)
    category = db.Column(db.Enum(Category), nullable=False, default=Category.UNKNOWN)

    def create(self):
        self.id = None
        db.session.add(self)
        db.session.commit()
        return self

    def update(self):
        if self.id is None:
            raise DataValidationError("Product must have an ID to update")
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        return dict(id=self.id, name=self.name, description=self.description,
                    price=str(self.price), available=self.available,
                    category=self.category.name)

    def deserialize(self, data):
        try:
            if not isinstance(data, dict):
                raise ValueError("Expected an object")
            name, description = data["name"], data["description"]
            if not isinstance(name, str) or not name.strip() or not isinstance(description, str):
                raise ValueError("Name and description must be strings")
            if type(data["available"]) is not bool:
                raise ValueError("Available must be a boolean")
            price = Decimal(str(data["price"]))
            if not price.is_finite() or price < 0 or price > Decimal("99999999.99"):
                raise ValueError("Price is out of range")
            category = Category[data["category"]]
            self.name, self.description = name, description
            self.price, self.available, self.category = price, data["available"], category
        except (KeyError, TypeError, ValueError, InvalidOperation) as error:
            raise DataValidationError(str(error)) from error
        return self

    @classmethod
    def find(cls, product_id):
        return db.session.get(cls, product_id)

    @classmethod
    def all(cls):
        return cls.query.order_by(cls.id).all()

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).all()

    @classmethod
    def find_by_category(cls, category):
        return cls.query.filter_by(category=category).all()

    @classmethod
    def find_by_availability(cls, available=True):
        return cls.query.filter_by(available=available).all()
