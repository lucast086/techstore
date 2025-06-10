"""Test cases for the users app models."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from users.models import Permission, Role
from users.models import User as CustomUser

User = get_user_model()


class TestUserModel(TestCase):
    """Test cases for the User model."""

    def setUp(self):
        """Set up test data."""
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }

    def test_create_user(self):
        """Test user creation with valid data."""
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertEqual(user.username, self.user_data["username"])
        self.assertEqual(user.email, self.user_data["email"])
        self.assertEqual(user.first_name, self.user_data["first_name"])
        self.assertEqual(user.last_name, self.user_data["last_name"])
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test superuser creation."""
        superuser = CustomUser.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin123"
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_user_str_representation(self):
        """Test string representation of user."""
        user = CustomUser.objects.create_user(**self.user_data)
        expected_str = f"{self.user_data['username']} ({self.user_data['email']})"
        self.assertEqual(str(user), expected_str)

    def test_user_with_role(self):
        """Test user creation and permission checking with role."""
        # Create role and permission
        role = Role.objects.create(name="Test Role", description="Role for testing")
        permission = Permission.objects.create(
            name="Test Permission", codename="test_permission", description="Permission for testing"
        )
        role.permissions.add(permission)

        # Create user with role
        user = CustomUser.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123", role=role
        )

        # Test role assignment
        self.assertEqual(user.role, role)
        self.assertTrue(user.has_tenant_permission("test_permission"))
        self.assertFalse(user.has_tenant_permission("non_existent"))
        self.assertEqual(user.get_tenant_permissions().count(), 1)

    def test_user_without_role(self):
        """Test user without role has no permissions."""
        user = CustomUser.objects.create_user(
            username="norole", email="norole@example.com", password="testpass123"
        )
        self.assertIsNone(user.role)
        self.assertFalse(user.has_tenant_permission("test_permission"))
        self.assertEqual(user.get_tenant_permissions().count(), 0)


class TestRoleModel(TestCase):
    """Test cases for the Role model."""

    def setUp(self):
        """Set up test data."""
        self.permission = Permission.objects.create(
            name="Test Permission", codename="test_permission", description="Permission for testing"
        )

    def test_create_role(self):
        """Test role creation."""
        role = Role.objects.create(name="Test Role", description="Role for testing")
        self.assertEqual(role.name, "Test Role")
        self.assertEqual(role.description, "Role for testing")
        self.assertEqual(role.permissions.count(), 0)

    def test_role_with_permissions(self):
        """Test role with permissions."""
        role = Role.objects.create(name="Test Role", description="Role for testing")
        role.permissions.add(self.permission)

        self.assertEqual(role.permissions.count(), 1)
        self.assertTrue(role.permissions.filter(codename="test_permission").exists())

    def test_role_str_representation(self):
        """Test string representation of role."""
        role = Role.objects.create(name="Test Role", description="Role for testing")
        self.assertEqual(str(role), "Test Role")


class TestPermissionModel(TestCase):
    """Test cases for the Permission model."""

    def test_create_permission(self):
        """Test permission creation."""
        permission = Permission.objects.create(
            name="Test Permission", codename="test_permission", description="Permission for testing"
        )
        self.assertEqual(permission.name, "Test Permission")
        self.assertEqual(permission.codename, "test_permission")
        self.assertEqual(permission.description, "Permission for testing")

    def test_permission_str_representation(self):
        """Test string representation of permission."""
        permission = Permission.objects.create(
            name="Test Permission", codename="test_permission", description="Permission for testing"
        )
        self.assertEqual(str(permission), "Test Permission")

    def test_permission_unique_codename(self):
        """Test that permission codename must be unique."""
        Permission.objects.create(
            name="Test Permission", codename="test_permission", description="Permission for testing"
        )

        with self.assertRaises(Exception):  # Should raise IntegrityError
            Permission.objects.create(
                name="Another Permission",
                codename="test_permission",  # Same codename
                description="Another permission",
            )
