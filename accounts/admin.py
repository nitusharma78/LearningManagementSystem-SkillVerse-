from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Student, Parent


class UserAdmin(BaseUserAdmin):
    list_display = [
        "get_full_name",
        "username",
        "email",
        "is_active",
        "is_student",
        "is_lecturer",
        "is_parent",
        "is_staff",
    ]
    search_fields = [
        "username",
        "first_name",
        "last_name",
        "email",
    ]
    list_filter = [
        "is_active",
        "is_student",
        "is_lecturer",
        "is_parent",
        "is_staff",
    ]
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'gender')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                  'is_student', 'is_lecturer', 'is_parent')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    ordering = ('email',)

class StudentAdmin(admin.ModelAdmin):
    list_display = ['student', 'level', 'program']
    search_fields = ['student__email', 'student__first_name', 'student__last_name']
    list_filter = ['level', 'program']

class ParentAdmin(admin.ModelAdmin):
    list_display = ['user', 'student', 'relation_ship']
    search_fields = ['user__email', 'student__student__email']
    list_filter = ['relation_ship']


admin.site.register(User, UserAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Parent, ParentAdmin)
