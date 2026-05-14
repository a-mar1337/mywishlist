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