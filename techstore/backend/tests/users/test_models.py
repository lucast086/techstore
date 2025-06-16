"""Test cases for the users app models."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django_tenants.test.cases import TenantTestCase
from users.models import UserAuditLog

User = get_user_model()


class TestUserModel(TenantTestCase):
    """Test cases for the User model."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }

    def test_create_user(self):
        """Test user creation with valid data."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, self.user_data["username"])
        self.assertEqual(user.email, self.user_data["email"])
        self.assertEqual(user.first_name, self.user_data["first_name"])
        self.assertEqual(user.last_name, self.user_data["last_name"])
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test superuser creation."""
        superuser = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin123"
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_user_str_representation(self):
        """Test string representation of user."""
        user = User.objects.create_user(**self.user_data)
        expected_str = f"{user.first_name} {user.last_name} ({user.email})"
        self.assertEqual(str(user), expected_str)

    def test_user_with_group(self):
        """Test user with group (role)."""
        # Create group
        group = Group.objects.create(name="Vendedor")

        # Create user and assign group
        user = User.objects.create_user(**self.user_data)
        user.groups.add(group)

        # Test group assignment
        self.assertTrue(user.has_role("Vendedor"))
        self.assertFalse(user.has_role("Administrador"))
        self.assertEqual(user.get_role(), group)

    def test_user_without_group(self):
        """Test user without group has no role."""
        user = User.objects.create_user(**self.user_data)
        self.assertIsNone(user.get_role())
        self.assertFalse(user.has_role("Vendedor"))

    def test_user_with_multiple_groups(self):
        """Test user with multiple groups returns first as primary role."""
        # Create groups
        group1 = Group.objects.create(name="Vendedor")
        group2 = Group.objects.create(name="Técnico")

        # Create user and assign groups
        user = User.objects.create_user(**self.user_data)
        user.groups.add(group1, group2)

        # Test that get_role returns the first group
        self.assertEqual(user.get_role().name, "Vendedor")
        self.assertTrue(user.has_role("Vendedor"))
        self.assertTrue(user.has_role("Técnico"))

    def test_user_phone_field(self):
        """Test user phone field."""
        user = User.objects.create_user(**self.user_data, phone="+1234567890")
        self.assertEqual(user.phone, "+1234567890")

    def test_get_full_name(self):
        """Test get_full_name method."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_full_name(), "Test User")

        # Test with no name
        user2 = User.objects.create_user(
            username="noname", email="noname@example.com", password="testpass123"
        )
        self.assertEqual(user2.get_full_name(), "noname")


class TestUserAuditLog(TenantTestCase):
    """Test cases for the UserAuditLog model."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_log_action(self):
        """Test logging a user action."""
        log = UserAuditLog.log_action(
            user=self.user, action="login", details={"method": "password"}
        )

        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, "login")
        self.assertEqual(log.details["method"], "password")
        self.assertIsNotNone(log.timestamp)

    def test_log_action_with_request(self):
        """Test logging with request information."""
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/test/")
        request.META["REMOTE_ADDR"] = "127.0.0.1"
        request.META["HTTP_USER_AGENT"] = "TestBrowser/1.0"

        log = UserAuditLog.log_action(
            user=self.user, action="page_view", details={"page": "/test/"}, request=request
        )

        self.assertEqual(log.ip_address, "127.0.0.1")
        self.assertEqual(log.user_agent, "TestBrowser/1.0")

    def test_audit_log_str_representation(self):
        """Test string representation of audit log."""
        log = UserAuditLog.log_action(user=self.user, action="test_action")
        expected_str = f"{self.user} - test_action - {log.timestamp}"
        self.assertEqual(str(log), expected_str)
