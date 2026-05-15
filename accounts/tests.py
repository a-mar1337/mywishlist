from django.test import TestCase
from django.urls import reverse

from .forms import EmailLoginForm, ProfileForm, RegisterForm
from .models import Profile, User


class UserModelTests(TestCase):
    def test_create_user_and_profile(self):
        user = User.objects.create_user(
            email="USER@Example.COM",
            password="StrongPass123"
        )

        self.assertEqual(user.email, "user@example.com")
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertEqual(str(user), "user@example.com")

    def test_profile_str(self):
        user = User.objects.create_user(
            email="profile@example.com",
            password="StrongPass123"
        )

        user.profile.display_name = "Иван"
        user.profile.save()

        self.assertEqual(str(user.profile), "Иван")


class AccountFormTests(TestCase):
    def test_register_form_valid(self):
        form = RegisterForm(data={
            "email": "new@example.com",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
        })

        self.assertTrue(form.is_valid())

    def test_register_form_invalid_password_mismatch(self):
        form = RegisterForm(data={
            "email": "new@example.com",
            "password1": "StrongPass123",
            "password2": "OtherPass123",
        })

        self.assertFalse(form.is_valid())

    def test_login_form_valid(self):
        User.objects.create_user(
            email="login@example.com",
            password="StrongPass123"
        )

        form = EmailLoginForm(data={
            "email": "login@example.com",
            "password": "StrongPass123",
        })

        self.assertTrue(form.is_valid())

    def test_login_form_invalid(self):
        form = EmailLoginForm(data={
            "email": "none@example.com",
            "password": "bad-password",
        })

        self.assertFalse(form.is_valid())

    def test_profile_form_invalid_short_name(self):
        form = ProfileForm(data={
            "display_name": "A",
            "bio": "Test bio",
        })

        self.assertFalse(form.is_valid())

    def test_register_form_save_sets_username(self):
        form = RegisterForm(data={
            "email": "saved@example.com",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
        })

        self.assertTrue(form.is_valid())

        user = form.save()

        self.assertEqual(user.email, "saved@example.com")
        self.assertEqual(user.username, "saved@example.com")


class AccountViewTests(TestCase):
    def test_register_view_status_and_template(self):
        response = self.client.get(reverse("accounts:register"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_login_view_status_and_template(self):
        response = self.client.get(reverse("accounts:login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_profile_requires_auth(self):
        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 302)

    def test_profile_available_for_auth_user(self):
        User.objects.create_user(
            email="auth@example.com",
            password="StrongPass123"
        )

        self.client.login(
            username="auth@example.com",
            password="StrongPass123"
        )

        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")

    def test_register_view_creates_user(self):
        response = self.client.post(reverse("accounts:register"), {
            "email": "view@example.com",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email="view@example.com").exists())

        user = User.objects.get(email="view@example.com")
        self.assertEqual(user.username, "view@example.com")