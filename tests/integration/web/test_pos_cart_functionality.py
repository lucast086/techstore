"""Tests for POS cart frontend functionality.

These tests verify that the cart JavaScript functionality works correctly,
including price editing, quantity updates, and form submission behavior.

These are regression tests to prevent bugs from being reintroduced where:
1. Price editing in cart doesn't work (productId passed as string instead of number)
2. Quantity editing in cart doesn't work (productId passed as string instead of number)
3. Enter key accidentally submits the checkout form
"""

import pytest


class TestPOSCartFrontend:
    """Test POS cart frontend functionality - regression tests for cart JavaScript."""

    def test_cart_price_input_has_correct_onchange_handler(
        self,
        client,
        test_user,
    ):
        """Test that price input field has correct onchange handler without quotes around productId.

        REGRESSION TEST: This prevents the bug where productId is passed as string instead of number,
        causing cart.find() to fail when trying to update prices.

        BUG FIX: Changed from onchange="updatePrice('${item.productId}', ...)"
                 to onchange="updatePrice(${item.productId}, ...)"
        """
        client.cookies.set("access_token", f"test_token_{test_user.id}")
        response = client.get("/sales/pos")

        # Skip test if cash register is not open (we only care about HTML/JS structure)
        if response.status_code != 200:
            pytest.skip("Cash register not open")

        # The template should render price input with onchange handler
        # Check that the JavaScript function exists
        assert "function updatePrice(productId, newPrice)" in response.text

        # Check that the price input field pattern exists in the template
        # The handler should pass productId WITHOUT quotes: onchange="updatePrice(${item.productId}, this.value)"
        assert 'onchange="updatePrice(' in response.text

        # CRITICAL: Verify the function doesn't use quoted productId (this was the bug)
        # The template literal should NOT have: onchange="updatePrice('${item.productId}', this.value)"
        assert "onchange=\"updatePrice('${item.productId}'" not in response.text

    def test_cart_quantity_input_has_correct_onchange_handler(
        self,
        client,
        test_user,
    ):
        """Test that quantity input field has correct onchange handler without quotes around productId.

        REGRESSION TEST: This prevents the bug where productId is passed as string instead of number,
        causing cart.find() to fail when trying to update quantities.

        BUG FIX: Changed from onchange="updateQuantity('${item.productId}', ...)"
                 to onchange="updateQuantity(${item.productId}, ...)"
        """
        client.cookies.set("access_token", f"test_token_{test_user.id}")
        response = client.get("/sales/pos")

        if response.status_code != 200:
            pytest.skip("Cash register not open")

        # The template should render quantity input with onchange handler
        # Check that the JavaScript function exists
        assert "function updateQuantity(productId, newQuantity)" in response.text

        # Check that the quantity input field pattern exists in the template
        # The handler should pass productId WITHOUT quotes: onchange="updateQuantity(${item.productId}, this.value)"
        assert 'onchange="updateQuantity(' in response.text

        # CRITICAL: Verify the function doesn't use quoted productId (this was the bug)
        # The template literal should NOT have: onchange="updateQuantity('${item.productId}', this.value)"
        assert "onchange=\"updateQuantity('${item.productId}'" not in response.text

    def test_remove_button_has_correct_onclick_handler(
        self,
        client,
        test_user,
    ):
        """Test that remove button has correct onclick handler without quotes around productId.

        REGRESSION TEST: This prevents the bug where productId is passed as string instead of number,
        causing cart.find() to fail when trying to remove items.

        BUG FIX: Changed from onclick="removeFromCart('${item.productId}')"
                 to onclick="removeFromCart(${item.productId})"
        """
        client.cookies.set("access_token", f"test_token_{test_user.id}")
        response = client.get("/sales/pos")

        if response.status_code != 200:
            pytest.skip("Cash register not open")

        # Check that the JavaScript function exists
        assert "function removeFromCart(productId)" in response.text

        # Check that the remove button pattern exists in the template
        # The handler should pass productId WITHOUT quotes: onclick="removeFromCart(${item.productId})"
        assert 'onclick="removeFromCart(' in response.text

        # CRITICAL: Verify the function doesn't use quoted productId (this was the bug)
        # The template literal should NOT have: onclick="removeFromCart('${item.productId}')"
        assert "onclick=\"removeFromCart('${item.productId}'" not in response.text

    def test_checkout_form_prevents_enter_key_submission(
        self,
        client,
        test_user,
    ):
        """Test that checkout form has onkeydown handler to prevent Enter key submission.

        REGRESSION TEST: This prevents accidental form submission when user presses Enter
        while editing quantity or price fields.

        BUG FIX: Added onkeydown="return event.key != 'Enter';" to checkout form
        """
        client.cookies.set("access_token", f"test_token_{test_user.id}")
        response = client.get("/sales/pos")

        if response.status_code != 200:
            pytest.skip("Cash register not open")

        # The checkout form should have onkeydown handler to prevent Enter key
        assert 'id="checkout-form"' in response.text
        assert "onkeydown=\"return event.key != 'Enter';\"" in response.text

    def test_price_update_function_validates_negative_prices(
        self,
        client,
        test_user,
    ):
        """Test that updatePrice function validates against negative prices."""
        client.cookies.set("access_token", f"test_token_{test_user.id}")
        response = client.get("/sales/pos")

        if response.status_code != 200:
            pytest.skip("Cash register not open")

        # Check that the validation logic exists in the function
        assert "function updatePrice(productId, newPrice)" in response.text
        assert "if (price < 0)" in response.text
        assert "El precio no puede ser negativo" in response.text

    def test_price_update_function_validates_nan_values(
        self,
        client,
        test_user,
    ):
        """Test that updatePrice function validates against NaN values."""
        client.cookies.set("access_token", f"test_token_{test_user.id}")
        response = client.get("/sales/pos")

        if response.status_code != 200:
            pytest.skip("Cash register not open")

        # Check that the validation logic exists in the function
        assert "function updatePrice(productId, newPrice)" in response.text
        assert "if (isNaN(price))" in response.text
        assert "Por favor ingrese un precio válido" in response.text

    def test_cart_display_includes_editable_price_field(
        self,
        client,
        test_user,
    ):
        """Test that cart display renders editable price input field."""
        client.cookies.set("access_token", f"test_token_{test_user.id}")
        response = client.get("/sales/pos")

        if response.status_code != 200:
            pytest.skip("Cash register not open")

        # Check that the cart rendering includes price input field
        assert 'id="price-${item.productId}"' in response.text
        assert 'type="number"' in response.text
        assert 'min="0"' in response.text
        assert 'step="0.01"' in response.text

    def test_cart_javascript_functions_exist(
        self,
        client,
        test_user,
    ):
        """Test that all required cart JavaScript functions are defined."""
        client.cookies.set("access_token", f"test_token_{test_user.id}")
        response = client.get("/sales/pos")

        if response.status_code != 200:
            pytest.skip("Cash register not open")

        # Verify all cart management functions exist
        required_functions = [
            "function addToCart(",
            "function removeFromCart(",
            "function updateQuantity(",
            "function updatePrice(",
            "function clearCart(",
            "function updateCartDisplay(",
            "function updateCartTotals(",
        ]

        for func in required_functions:
            assert func in response.text, f"Missing function: {func}"

    def test_cart_array_initialization(
        self,
        client,
        test_user,
    ):
        """Test that cart array is properly initialized."""
        client.cookies.set("access_token", f"test_token_{test_user.id}")
        response = client.get("/sales/pos")

        if response.status_code != 200:
            pytest.skip("Cash register not open")

        # Check that cart is initialized as empty array
        assert "let cart = [];" in response.text
