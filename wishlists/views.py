import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AssignExecutorForm, ItemCommentForm, WishlistForm, WishlistItemForm
from .models import ItemComment, Wishlist, WishlistAccess, WishlistItem


def user_can_access_wishlist(user, wishlist):
    if not user.is_authenticated:
        return False

    if wishlist.owner == user:
        return True

    return WishlistAccess.objects.filter(wishlist=wishlist, user=user).exists()


@login_required
def dashboard_view(request):
    own_wishlists = Wishlist.objects.filter(owner=request.user)
    assigned_wishlists = Wishlist.objects.filter(executors=request.user)

    context = {
        "own_wishlists": own_wishlists,
        "assigned_wishlists": assigned_wishlists,
    }

    return render(request, "wishlists/dashboard.html", context)


@login_required
def wishlist_detail_view(request, pk):
    wishlist = get_object_or_404(Wishlist, pk=pk)

    if not user_can_access_wishlist(request.user, wishlist):
        raise PermissionDenied

    assign_form = AssignExecutorForm(wishlist=wishlist)
    comment_form = ItemCommentForm()

    context = {
        "wishlist": wishlist,
        "items": wishlist.items.all(),
        "accesses": wishlist.accesses.select_related("user"),
        "assign_form": assign_form,
        "comment_form": comment_form,
        "is_owner": wishlist.owner == request.user,
    }

    return render(request, "wishlists/wishlist_detail.html", context)


@login_required
def wishlist_create_view(request):
    if request.method == "POST":
        form = WishlistForm(request.POST)

        if form.is_valid():
            wishlist = form.save(commit=False)
            wishlist.owner = request.user
            wishlist.save()
            messages.success(request, "Вишлист создан.")
            return redirect("wishlists:wishlist_detail", pk=wishlist.pk)
    else:
        form = WishlistForm()

    return render(request, "wishlists/wishlist_form.html", {"form": form})


@login_required
def wishlist_update_view(request, pk):
    wishlist = get_object_or_404(Wishlist, pk=pk, owner=request.user)

    if request.method == "POST":
        form = WishlistForm(request.POST, instance=wishlist)

        if form.is_valid():
            form.save()
            messages.success(request, "Вишлист обновлён.")
            return redirect("wishlists:wishlist_detail", pk=wishlist.pk)
    else:
        form = WishlistForm(instance=wishlist)

    return render(request, "wishlists/wishlist_form.html", {"form": form, "wishlist": wishlist})


@login_required
def wishlist_delete_view(request, pk):
    wishlist = get_object_or_404(Wishlist, pk=pk, owner=request.user)

    if request.method == "POST":
        wishlist.delete()
        messages.success(request, "Вишлист удалён.")
        return redirect("wishlists:dashboard")

    return render(request, "wishlists/confirm_delete.html", {"object": wishlist})