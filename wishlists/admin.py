from django.contrib import admin

from .models import ItemComment, Wishlist, WishlistAccess, WishlistItem


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0


class WishlistAccessInline(admin.TabularInline):
    model = WishlistAccess
    extra = 0


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("title", "description", "owner__email")
    inlines = [WishlistItemInline, WishlistAccessInline]


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("title", "wishlist", "status", "priority", "approximate_price", "created_at")
    list_filter = ("status", "priority", "created_at")
    search_fields = ("title", "description", "wishlist__title")


@admin.register(WishlistAccess)
class WishlistAccessAdmin(admin.ModelAdmin):
    list_display = ("wishlist", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("wishlist__title", "user__email")


@admin.register(ItemComment)
class ItemCommentAdmin(admin.ModelAdmin):
    list_display = ("item", "author", "created_at")
    list_filter = ("created_at",)
    search_fields = ("item__title", "author__email", "text")