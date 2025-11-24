from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # This controls what fields are displayed in the list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    
    # This adds 'role' to the editable fields in the admin panel
    # We have to unpack the original fieldsets and add our custom one
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Role', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Role', {'fields': ('role',)}),
    )

admin.site.register(User, CustomUserAdmin)