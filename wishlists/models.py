from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Wishlist(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlists",
        verbose_name="Владелец",
    )
    title = models.CharField(
        max_length=150,
        verbose_name="Название",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )
    executors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="WishlistAccess",
        related_name="assigned_wishlists",
        blank=True,
        verbose_name="Исполнители",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления",
    )

    class Meta:
        verbose_name = "Вишлист"
        verbose_name_plural = "Вишлисты"
        ordering = ["-created_at"]

    def clean(self):
        if self.title and len(self.title.strip()) < 2:
            raise ValidationError("Название вишлиста должно содержать минимум 2 символа.")

    def __str__(self):
        return self.title


class WishlistAccess(models.Model):
    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name="accesses",
        verbose_name="Вишлист",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_accesses",
        verbose_name="Пользователь",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата назначения",
    )

    class Meta:
        verbose_name = "Доступ к вишлисту"
        verbose_name_plural = "Доступы к вишлистам"
        unique_together = ("wishlist", "user")
        ordering = ["-created_at"]

    def clean(self):
        if self.wishlist and self.user and self.wishlist.owner == self.user:
            raise ValidationError("Владелец не может быть исполнителем своего вишлиста.")

    def __str__(self):
        return f"{self.user} → {self.wishlist}"


class WishlistItem(models.Model):
    STATUS_NOT_DONE = "not_done"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_DONE = "done"

    STATUS_CHOICES = [
        (STATUS_NOT_DONE, "Не выполнено"),
        (STATUS_IN_PROGRESS, "В процессе"),
        (STATUS_DONE, "Выполнено"),
    ]

    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Низкий"),
        (PRIORITY_MEDIUM, "Средний"),
        (PRIORITY_HIGH, "Высокий"),
    ]

    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Вишлист",
    )
    title = models.CharField(
        max_length=150,
        verbose_name="Название",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )
    product_url = models.URLField(
        blank=True,
        verbose_name="Ссылка на товар",
    )
    approximate_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Примерная цена",
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
        verbose_name="Приоритет",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NOT_DONE,
        verbose_name="Статус",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления",
    )

    class Meta:
        verbose_name = "Желание"
        verbose_name_plural = "Желания"
        ordering = ["-created_at"]

    @property
    def is_done(self):
        return self.status == self.STATUS_DONE

    def clean(self):
        if self.title and len(self.title.strip()) < 2:
            raise ValidationError("Название желания должно содержать минимум 2 символа.")

    def __str__(self):
        return self.title


class ItemComment(models.Model):
    item = models.ForeignKey(
        WishlistItem,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Желание",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="item_comments",
        verbose_name="Автор",
    )
    text = models.TextField(
        verbose_name="Комментарий",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["created_at"]

    def clean(self):
        if self.text and len(self.text.strip()) < 2:
            raise ValidationError("Комментарий должен содержать минимум 2 символа.")

    def __str__(self):
        return f"Комментарий от {self.author}"