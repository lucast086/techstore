"""Management command to set up initial roles (groups) for the system."""

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    """Set up initial roles and permissions for the system."""

    help = "Creates initial roles (groups) with their default permissions"

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write("Setting up initial roles...")

        with transaction.atomic():
            # Define roles and their permissions
            roles_config = {
                "Administrador": {
                    "description": "Full system access",
                    "permissions": [
                        # User management
                        "add_user",
                        "change_user",
                        "delete_user",
                        "view_user",
                        # Group management
                        "add_group",
                        "change_group",
                        "delete_group",
                        "view_group",
                        # Audit logs
                        "view_userauditlog",
                    ],
                },
                "Vendedor": {
                    "description": "Sales and customer management",
                    "permissions": [
                        # Limited user access
                        "view_user",
                        # Audit logs (view only)
                        "view_userauditlog",
                    ],
                },
                "Técnico": {
                    "description": "Technical service management",
                    "permissions": [
                        # Limited user access
                        "view_user",
                        # Audit logs (view only)
                        "view_userauditlog",
                    ],
                },
            }

            for role_name, config in roles_config.items():
                # Create or get the group
                group, created = Group.objects.get_or_create(name=role_name)

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created role: {role_name}"))
                else:
                    self.stdout.write(f"Role already exists: {role_name}")

                # Clear existing permissions
                group.permissions.clear()

                # Add permissions
                for perm_codename in config["permissions"]:
                    try:
                        # Find the permission
                        app_label, codename = perm_codename.rsplit("_", 1)
                        if app_label == "add":
                            app_label = "users"
                            codename = f"add_{codename}"
                        elif app_label == "change":
                            app_label = "users"
                            codename = f"change_{codename}"
                        elif app_label == "delete":
                            app_label = "users"
                            codename = f"delete_{codename}"
                        elif app_label == "view":
                            app_label = "users"
                            codename = f"view_{codename}"
                        else:
                            # For permissions like view_userauditlog
                            parts = perm_codename.split("_", 1)
                            if len(parts) == 2:
                                action, model = parts
                                app_label = "users"
                                codename = perm_codename

                        permission = Permission.objects.get(
                            codename=codename,
                            content_type__app_label=app_label,
                        )
                        group.permissions.add(permission)

                    except Permission.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f"Permission not found: {perm_codename}")
                        )

                self.stdout.write(f"  Added {group.permissions.count()} permissions to {role_name}")

        self.stdout.write(self.style.SUCCESS("Successfully set up all roles!"))
