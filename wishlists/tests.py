from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from .forms import AssignExecutorForm, ItemCommentForm, WishlistForm, WishlistItemForm
from .models import ItemComment, Wishlist, WishlistAccess, WishlistItem


class WishlistModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="StrongPass123"
        )
        self.executor = User.objects.create_user(
            email="executor@example.com",
            password="StrongPass123"
        )

    def test_create_wishlist(self):
        wishlist = Wishlist.objects.create(
            owner=self.owner,
            title="День рождения",
            description="Подарки на день рождения"
        )

        self.assertEqual(wishlist.title, "День рождения")
        self.assertEqual(wishlist.owner, self.owner)
        self.assertEqual(str(wishlist), "День рождения")

    def test_wishlist_title_validation(self):
        wishlist = Wishlist(
            owner=self.owner,
            title="A",
            description="Test"
        )

        with self.assertRaises(ValidationError):
            wishlist.full_clean()

    def test_create_item_and_methods(self):
        wishlist = Wishlist.objects.create(
            owner=self.owner,
            title="Wishlist"
        )

        item = WishlistItem.objects.create(
            wishlist=wishlist,
            title="Наушники",
            approximate_price=Decimal("5000.00"),
            status=WishlistItem.STATUS_DONE,
        )

        self.assertEqual(str(item), "Наушники")
        self.assertTrue(item.is_done)
        self.assertEqual(item.approximate_price, Decimal("5000.00"))

    def test_item_negative_price_invalid(self):
        wishlist = Wishlist.objects.create(
            owner=self.owner,
            title="Wishlist"
        )

        item = WishlistItem(
            wishlist=wishlist,
            title="Item",
            approximate_price=Decimal("-1.00"),
        )

        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_wishlist_access_many_to_many(self):
        wishlist = Wishlist.objects.create(
            owner=self.owner,
            title="Wishlist"
        )

        WishlistAccess.objects.create(
            wishlist=wishlist,
            user=self.executor
        )

        self.assertIn(self.executor, wishlist.executors.all())

    def test_owner_cannot_be_executor(self):
        wishlist = Wishlist.objects.create(
            owner=self.owner,
            title="Wishlist"
        )

        access = WishlistAccess(
            wishlist=wishlist,
            user=self.owner
        )

        with self.assertRaises(ValidationError):
            access.full_clean()

    def test_comment_create_and_str(self):
        wishlist = Wishlist.objects.create(
            owner=self.owner,
            title="Wishlist"
        )
        item = WishlistItem.objects.create(
            wishlist=wishlist,
            title="Книга"
        )

        comment = ItemComment.objects.create(
            item=item,
            author=self.executor,
            text="Куплю позже"
        )

        self.assertEqual(comment.text, "Куплю позже")
        self.assertEqual(str(comment), "Комментарий от executor@example.com")


class WishlistFormTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="StrongPass123"
        )
        self.executor = User.objects.create_user(
            email="executor@example.com",
            password="StrongPass123"
        )
        self.wishlist = Wishlist.objects.create(
            owner=self.owner,
            title="Wishlist"
        )

    def test_wishlist_form_valid(self):
        form = WishlistForm(data={
            "title": "Мой список",
            "description": "Описание",
        })

        self.assertTrue(form.is_valid())

    def test_wishlist_form_invalid_short_title(self):
        form = WishlistForm(data={
            "title": "A",
            "description": "Описание",
        })

        self.assertFalse(form.is_valid())

    def test_item_form_valid_required_fields(self):
        form = WishlistItemForm(data={
            "title": "Книга",
            "description": "",
            "product_url": "",
            "approximate_price": "",
            "priority": WishlistItem.PRIORITY_MEDIUM,
            "status": WishlistItem.STATUS_NOT_DONE,
        })

        self.assertTrue(form.is_valid())

    def test_item_form_invalid_url(self):
        form = WishlistItemForm(data={
            "title": "Книга",
            "description": "",
            "product_url": "not-url",
            "approximate_price": "",
            "priority": WishlistItem.PRIORITY_MEDIUM,
            "status": WishlistItem.STATUS_NOT_DONE,
        })

        self.assertFalse(form.is_valid())

    def test_assign_executor_form_valid(self):
        form = AssignExecutorForm(
            data={"email": "executor@example.com"},
            wishlist=self.wishlist
        )

        self.assertTrue(form.is_valid())

    def test_assign_executor_form_invalid_unknown_user(self):
        form = AssignExecutorForm(
            data={"email": "none@example.com"},
            wishlist=self.wishlist
        )

        self.assertFalse(form.is_valid())

    def test_comment_form_valid(self):
        form = ItemCommentForm(data={
            "text": "Хорошая идея"
        })

        self.assertTrue(form.is_valid())

    def test_comment_form_invalid_short_text(self):
        form = ItemCommentForm(data={
            "text": "A"
        })

        self.assertFalse(form.is_valid())

class WishlistViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="StrongPass123"
        )
        self.executor = User.objects.create_user(
            email="executor@example.com",
            password="StrongPass123"
        )
        self.other = User.objects.create_user(
            email="other@example.com",
            password="StrongPass123"
        )

        self.wishlist = Wishlist.objects.create(
            owner=self.owner,
            title="Birthday"
        )

        self.item = WishlistItem.objects.create(
            wishlist=self.wishlist,
            title="Headphones",
            status=WishlistItem.STATUS_NOT_DONE,
        )

        WishlistAccess.objects.create(
            wishlist=self.wishlist,
            user=self.executor
        )

    def test_dashboard_requires_auth(self):
        response = self.client.get(reverse("wishlists:dashboard"))

        self.assertEqual(response.status_code, 302)

    def test_dashboard_for_auth_user(self):
        self.client.login(
            username="owner@example.com",
            password="StrongPass123"
        )

        response = self.client.get(reverse("wishlists:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wishlists/dashboard.html")

    def test_owner_can_view_wishlist(self):
        self.client.login(
            username="owner@example.com",
            password="StrongPass123"
        )

        response = self.client.get(
            reverse("wishlists:wishlist_detail", kwargs={"pk": self.wishlist.pk})
        )

        self.assertEqual(response.status_code, 200)

    def test_executor_can_view_wishlist(self):
        self.client.login(
            username="executor@example.com",
            password="StrongPass123"
        )

        response = self.client.get(
            reverse("wishlists:wishlist_detail", kwargs={"pk": self.wishlist.pk})
        )

        self.assertEqual(response.status_code, 200)

    def test_other_user_cannot_view_wishlist(self):
        self.client.login(
            username="other@example.com",
            password="StrongPass123"
        )

        response = self.client.get(
            reverse("wishlists:wishlist_detail", kwargs={"pk": self.wishlist.pk})
        )

        self.assertEqual(response.status_code, 403)

    def test_owner_can_create_item(self):
        self.client.login(
            username="owner@example.com",
            password="StrongPass123"
        )

        response = self.client.post(
            reverse("wishlists:item_create", kwargs={"wishlist_pk": self.wishlist.pk}),
            {
                "title": "Мышка",
                "description": "",
                "product_url": "",
                "approximate_price": "",
                "priority": WishlistItem.PRIORITY_MEDIUM,
                "status": WishlistItem.STATUS_NOT_DONE,
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(WishlistItem.objects.filter(title="Мышка").exists())

    def test_executor_can_update_status(self):
        self.client.login(
            username="executor@example.com",
            password="StrongPass123"
        )

        response = self.client.post(
            reverse("wishlists:item_update", kwargs={"pk": self.item.pk}),
            {
                "title": self.item.title,
                "description": self.item.description,
                "product_url": self.item.product_url,
                "approximate_price": "",
                "priority": WishlistItem.PRIORITY_MEDIUM,
                "status": WishlistItem.STATUS_DONE,
            }
        )

        self.item.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.item.status, WishlistItem.STATUS_DONE)

    def test_anonymous_cannot_export_csv(self):
        response = self.client.get(
            reverse("wishlists:export_csv", kwargs={"pk": self.wishlist.pk})
        )

        self.assertEqual(response.status_code, 302)

    def test_owner_can_export_csv(self):
        self.client.login(
            username="owner@example.com",
            password="StrongPass123"
        )

        response = self.client.get(
            reverse("wishlists:export_csv", kwargs={"pk": self.wishlist.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")

    def test_add_comment(self):
        self.client.login(
            username="executor@example.com",
            password="StrongPass123"
        )

        response = self.client.post(
            reverse("wishlists:add_comment", kwargs={"item_pk": self.item.pk}),
            {
                "text": "Сделаю позже"
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(ItemComment.objects.filter(text="Сделаю позже").exists())