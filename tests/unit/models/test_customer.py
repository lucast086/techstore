"""Unit tests for Customer model."""

import pytest
from app.models.customer import Customer
from sqlalchemy.exc import IntegrityError


class TestCustomerModel:
    """Test cases for Customer model."""

    def test_create_customer_with_required_fields(self, db_session):
        """Test creating a customer with only required fields."""
        customer = Customer(name="John Doe", phone="1234567890")
        db_session.add(customer)
        db_session.commit()

        assert customer.id is not None
        assert customer.name == "John Doe"
        assert customer.phone == "1234567890"
        assert customer.is_active is True
        assert customer.created_at is not None
        assert customer.updated_at is not None

    def test_create_customer_with_all_fields(self, db_session, test_user):
        """Test creating a customer with all fields."""
        customer = Customer(
            name="Jane Smith",
            phone="0987654321",
            phone_secondary="1112223333",
            email="jane@example.com",
            address="123 Main St",
            notes="VIP customer",
            created_by_id=test_user.id,
        )
        db_session.add(customer)
        db_session.commit()

        assert customer.id is not None
        assert customer.name == "Jane Smith"
        assert customer.phone == "0987654321"
        assert customer.phone_secondary == "1112223333"
        assert customer.email == "jane@example.com"
        assert customer.address == "123 Main St"
        assert customer.notes == "VIP customer"
        assert customer.created_by_id == test_user.id
        assert customer.created_by == test_user

    def test_customer_name_required(self, db_session):
        """Test that customer name is required."""
        customer = Customer(phone="1234567890")
        db_session.add(customer)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_customer_phone_required(self, db_session):
        """Test that customer phone is required."""
        customer = Customer(name="John Doe")
        db_session.add(customer)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_display_phones_property(self, db_session):
        """Test display_phones property."""
        # Customer with only primary phone
        customer1 = Customer(name="John", phone="1111111111")
        assert customer1.display_phones == "1111111111"

        # Customer with both phones
        customer2 = Customer(
            name="Jane", phone="2222222222", phone_secondary="3333333333"
        )
        assert customer2.display_phones == "2222222222 / 3333333333"

    def test_search_string_property(self, db_session):
        """Test search_string property for search optimization."""
        customer = Customer(
            name="John Doe",
            phone="1234567890",
            phone_secondary="0987654321",
            email="john@example.com",
        )

        search_string = customer.search_string
        assert "john doe" in search_string
        assert "1234567890" in search_string
        assert "0987654321" in search_string
        assert "john@example.com" in search_string

    def test_to_dict_method(self, db_session, test_user):
        """Test to_dict method returns proper dictionary."""
        customer = Customer(
            name="Test Customer",
            phone="5555555555",
            email="test@example.com",
            created_by_id=test_user.id,
        )
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)

        customer_dict = customer.to_dict()

        assert customer_dict["id"] == customer.id
        assert customer_dict["name"] == "Test Customer"
        assert customer_dict["phone"] == "5555555555"
        assert customer_dict["email"] == "test@example.com"
        assert customer_dict["is_active"] is True
        assert customer_dict["created_by"] == test_user.full_name
        assert customer_dict["created_at"] is not None
        assert customer_dict["updated_at"] is not None

    def test_soft_delete(self, db_session):
        """Test soft delete functionality."""
        customer = Customer(name="Delete Me", phone="9999999999")
        db_session.add(customer)
        db_session.commit()

        # Soft delete
        customer.is_active = False
        db_session.commit()

        # Customer still exists but is inactive
        assert customer.id is not None
        assert customer.is_active is False

    def test_customer_repr(self, db_session):
        """Test string representation of customer."""
        customer = Customer(name="John Doe", phone="1234567890")
        assert repr(customer) == "<Customer John Doe - 1234567890>"

    def test_customer_relationships(self, db_session, test_user):
        """Test customer relationships with other models."""
        customer = Customer(
            name="Related Customer", phone="7777777777", created_by_id=test_user.id
        )
        db_session.add(customer)
        db_session.commit()

        # Test relationship navigation
        assert customer.created_by == test_user
        assert customer in test_user.created_customers
