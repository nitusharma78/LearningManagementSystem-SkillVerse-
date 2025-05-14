from django import forms
from django.db import transaction
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    AuthenticationForm,
)
from django.contrib.auth.forms import PasswordResetForm
from course.models import Program
from .models import User, Student, Parent, RELATION_SHIP, LEVEL, GENDERS


class BaseUserForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "type": "email",
                "class": "form-control",
                "placeholder": "Enter email address"
            }
        ),
        label="Email Address",
        required=True
    )

    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
                "placeholder": "Enter first name"
            }
        ),
        label="First Name",
        required=True
    )

    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
                "placeholder": "Enter last name"
            }
        ),
        label="Last Name",
        required=True
    )

    gender = forms.CharField(
        widget=forms.Select(
            choices=GENDERS,
            attrs={
                "class": "form-control"
            }
        ),
        required=False
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2', 'gender']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.gender = self.cleaned_data.get('gender')
        if commit:
            user.save()
        return user


class StudentAddForm(BaseUserForm):
    program = forms.ModelChoiceField(
        queryset=Program.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "placeholder": "Select program"
            }
        ),
        required=True,
        label="Program"
    )

    level = forms.CharField(
        widget=forms.Select(
            choices=LEVEL,
            attrs={
                "class": "form-control",
                "placeholder": "Select level"
            }
        ),
        required=True,
        label="Level"
    )

    class Meta(BaseUserForm.Meta):
        fields = BaseUserForm.Meta.fields + ['program', 'level']

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        if commit:
            user.save()
        return user


class StaffAddForm(BaseUserForm):
    phone = forms.CharField(
        max_length=60,
        widget=forms.TextInput(
            attrs={
                "type": "tel",
                "class": "form-control",
                "placeholder": "Enter phone number"
            }
        ),
        required=False
    )

    address = forms.CharField(
        max_length=60,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
                "placeholder": "Enter address"
            }
        ),
        required=False
    )

    class Meta(BaseUserForm.Meta):
        fields = BaseUserForm.Meta.fields + ['phone', 'address']

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_lecturer = True
        user.phone = self.cleaned_data.get('phone')
        user.address = self.cleaned_data.get('address')
        if commit:
            user.save()
        return user


class CombinedRegistrationForm(BaseUserForm):
    # Student fields
    program = forms.ModelChoiceField(
        queryset=Program.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "placeholder": "Select program"
            }
        ),
        required=False,
        label="Program"
    )

    level = forms.CharField(
        widget=forms.Select(
            choices=LEVEL,
            attrs={
                "class": "form-control"
            }
        ),
        required=False
    )

    # Lecturer fields
    phone = forms.CharField(
        max_length=60,
        widget=forms.TextInput(
            attrs={
                "type": "tel",
                "class": "form-control",
                "placeholder": "Enter phone number"
            }
        ),
        required=False
    )

    address = forms.CharField(
        max_length=60,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
                "placeholder": "Enter address"
            }
        ),
        required=False
    )

    class Meta(BaseUserForm.Meta):
        fields = BaseUserForm.Meta.fields + ['program', 'level', 'phone', 'address']

    def clean(self):
        cleaned_data = super().clean()
        role = self.data.get('selected_role')
        
        if role == 'student':
            if not cleaned_data.get('program'):
                self.add_error('program', 'Program is required for students')
            if not cleaned_data.get('level'):
                self.add_error('level', 'Level is required for students')
        elif role == 'lecturer':
            if not cleaned_data.get('phone'):
                self.add_error('phone', 'Phone number is required for lecturers')
            if not cleaned_data.get('address'):
                self.add_error('address', 'Address is required for lecturers')
        
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.data.get('selected_role')
        
        if commit:
            user.save()
            
            if role == 'student':
                Student.objects.create(
                    student=user,
                    program=self.cleaned_data.get('program'),
                    level=self.cleaned_data.get('level')
                )
                user.is_student = True
            elif role == 'lecturer':
                user.phone = self.cleaned_data.get('phone')
                user.address = self.cleaned_data.get('address')
                user.is_lecturer = True
                user.save(update_fields=['phone', 'address', 'is_lecturer'])
                
        return user


class ProfileUpdateForm(UserChangeForm):
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "class": "form-control",
            }
        ),
        label="Email Address",
    )

    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="First Name",
    )

    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Last Name",
    )

    gender = forms.CharField(
        widget=forms.Select(
            choices=GENDERS,
            attrs={
                "class": "browser-default custom-select form-control",
            },
        ),
    )

    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Phone No.",
    )

    address = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Address / city",
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "gender",
            "email",
            "phone",
            "address",
            "picture",
        ]


class ProgramUpdateForm(UserChangeForm):
    program = forms.ModelChoiceField(
        queryset=Program.objects.all(),
        widget=forms.Select(
            attrs={"class": "browser-default custom-select form-control"}
        ),
        label="Program",
    )

    class Meta:
        model = Student
        fields = ["program"]


class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            msg = "There is no user registered with the specified E-mail address. "
            self.add_error("email", msg)
            return email


class ParentAddForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "type": "email",
                "class": "form-control",
                "placeholder": "Enter your email"
            }
        ),
        label="Email Address",
        required=True
    )

    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="First name",
    )

    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Last name",
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter password"
            }
        ),
        label="Password"
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm password"
            }
        ),
        label="Confirm Password"
    )

    address = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Address",
    )

    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Mobile No.",
    )

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=forms.Select(
            attrs={"class": "browser-default custom-select form-control"}
        ),
        label="Student",
    )

    relation_ship = forms.CharField(
        widget=forms.Select(
            choices=RELATION_SHIP,
            attrs={
                "class": "browser-default custom-select form-control",
            },
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['email', 'password1', 'password2', 'first_name', 'last_name']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email  # Set username same as email
        user.is_parent = True
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.address = self.cleaned_data.get("address")
        user.phone = self.cleaned_data.get("phone")
        if commit:
            user.save()
            parent = Parent.objects.create(
                user=user,
                student=self.cleaned_data.get("student"),
                relation_ship=self.cleaned_data.get("relation_ship"),
            )
            parent.save()
        return user


class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email',
                'type': 'email'
            }
        ),
        label='Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your password',
            }
        ),
        label='Password'
    )

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            # Get the first user with this email
            try:
                user = User.objects.filter(email=email).first()
                if user:
                    self.cleaned_data['username'] = user.username
                else:
                    raise forms.ValidationError("Invalid email or password.")
            except User.DoesNotExist:
                raise forms.ValidationError("Invalid email or password.")

        return super().clean()
