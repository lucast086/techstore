"""Management command to set up initial roles and permissions for tenants."""

from django.core.management.base import BaseCommand
from users.models import Permission, Role


class Command(BaseCommand):
    """Command to set up initial roles and permissions for tenants."""

    help = "Sets up initial roles and permissions for tenants"

    def handle(self, *args, **options):
        """Execute the command to set up roles and permissions.

        Creates a set of predefined roles and permissions that will be available
        for all tenants in the system.
        """
        # Define permissions
        permissions = {
            # Sales permissions
            "view_sales": "Can view sales data",
            "create_sale": "Can create new sales",
            "edit_sale": "Can edit existing sales",
            "delete_sale": "Can delete sales",
            "view_sales_reports": "Can view sales reports",
            # Inventory permissions
            "view_inventory": "Can view inventory data",
            "edit_inventory": "Can edit inventory data",
            "manage_inventory": "Can manage inventory settings",
            # Technical support permissions
            "view_technical": "Can view technical support data",
            "create_technical": "Can create technical support tickets",
            "edit_technical": "Can edit technical support tickets",
            "resolve_technical": "Can resolve technical support tickets",
            # User management permissions
            "view_users": "Can view user data",
            "create_user": "Can create new users",
            "edit_user": "Can edit user data",
            "delete_user": "Can delete users",
            # Settings permissions
            "view_settings": "Can view tenant settings",
            "edit_settings": "Can edit tenant settings",
        }

        # Create permissions
        created_permissions = {}
        for codename, description in permissions.items():
            permission, created = Permission.objects.get_or_create(
                codename=codename,
                defaults={
                    "name": description,
                    "description": description,
                },
            )
            created_permissions[codename] = permission
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created permission "{codename}"'))

        # Define roles and their permissions
        roles = {
            "Tenant Admin": [
                "view_sales",
                "create_sale",
                "edit_sale",
                "delete_sale",
                "view_sales_reports",
                "view_inventory",
                "edit_inventory",
                "manage_inventory",
                "view_technical",
                "create_technical",
                "edit_technical",
                "resolve_technical",
                "view_users",
                "create_user",
                "edit_user",
                "delete_user",
                "view_settings",
                "edit_settings",
            ],
            "Sales Staff": [
                "view_sales",
                "create_sale",
                "edit_sale",
                "view_sales_reports",
                "view_inventory",
            ],
            "Technical Staff": [
                "view_technical",
                "create_technical",
                "edit_technical",
                "resolve_technical",
                "view_inventory",
            ],
            "Customer": ["view_sales", "create_technical"],
            "Manager": [
                "view_sales",
                "create_sale",
                "edit_sale",
                "delete_sale",
                "view_sales_reports",
                "view_inventory",
                "edit_inventory",
                "manage_inventory",
                "view_technical",
                "create_technical",
                "edit_technical",
                "resolve_technical",
                "view_users",
                "create_user",
                "edit_user",
                "delete_user",
            ],
        }

        # Create roles and assign permissions
        for role_name, permission_codenames in roles.items():
            role, created = Role.objects.get_or_create(
                name=role_name, defaults={"description": f"Role for {role_name}"}
            )

            # Clear existing permissions and add new ones
            role.permissions.clear()
            for codename in permission_codenames:
                role.permissions.add(created_permissions[codename])

            if created:
                self.stdout.write(self.style.SUCCESS(f'Created role "{role_name}"'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated role "{role_name}"'))

        self.stdout.write(self.style.SUCCESS("Successfully set up roles and permissions"))
