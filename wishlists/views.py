import csv
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .forms import AssignExecutorForm, ItemCommentForm, WishlistForm, WishlistItemForm
from .models import Wishlist, WishlistAccess, WishlistItem


logger = logging.getLogger(__name__)


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

    logger.info("Dashboard opened by user: %s", request.user.email)

    context = {
        "own_wishlists": own_wishlists,
        "assigned_wishlists": assigned_wishlists,
    }

    return render(request, "wishlists/dashboard.html", context)


@login_required
def wishlist_detail_view(request, pk):
    wishlist = get_object_or_404(Wishlist, pk=pk)

    if not user_can_access_wishlist(request.user, wishlist):
        logger.warning(
            "Forbidden wishlist access: wishlist_id=%s, user=%s",
            wishlist.id,
            request.user.email,
        )
        raise PermissionDenied

    logger.info(
        "Wishlist viewed: id=%s, user=%s",
        wishlist.id,
        request.user.email,
    )

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

            logger.info(
                "Wishlist created: id=%s, title=%s, owner=%s",
                wishlist.id,
                wishlist.title,
                request.user.email,
            )

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
            wishlist = form.save()

            logger.info(
                "Wishlist updated: id=%s, title=%s, user=%s",
                wishlist.id,
                wishlist.title,
                request.user.email,
            )

            messages.success(request, "Вишлист обновлён.")
            return redirect("wishlists:wishlist_detail", pk=wishlist.pk)
    else:
        form = WishlistForm(instance=wishlist)

    return render(
        request,
        "wishlists/wishlist_form.html",
        {
            "form": form,
            "wishlist": wishlist,
        },
    )


@login_required
def wishlist_delete_view(request, pk):
    wishlist = get_object_or_404(Wishlist, pk=pk, owner=request.user)

    if request.method == "POST":
        logger.warning(
            "Wishlist deleted: id=%s, title=%s, user=%s",
            wishlist.id,
            wishlist.title,
            request.user.email,
        )

        wishlist.delete()
        messages.success(request, "Вишлист удалён.")
        return redirect("wishlists:dashboard")

    return render(request, "wishlists/confirm_delete.html", {"object": wishlist})


@login_required
def item_create_view(request, wishlist_pk):
    wishlist = get_object_or_404(Wishlist, pk=wishlist_pk, owner=request.user)

    if request.method == "POST":
        form = WishlistItemForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.wishlist = wishlist
            item.save()

            logger.info(
                "Wishlist item created: id=%s, title=%s, wishlist_id=%s, user=%s",
                item.id,
                item.title,
                wishlist.id,
                request.user.email,
            )

            messages.success(request, "Желание добавлено.")
            return redirect("wishlists:wishlist_detail", pk=wishlist.pk)
    else:
        form = WishlistItemForm()

    return render(
        request,
        "wishlists/item_form.html",
        {
            "form": form,
            "wishlist": wishlist,
        },
    )


@login_required
def item_update_view(request, pk):
    item = get_object_or_404(WishlistItem, pk=pk)
    wishlist = item.wishlist

    if not user_can_access_wishlist(request.user, wishlist):
        logger.warning(
            "Forbidden item update: item_id=%s, wishlist_id=%s, user=%s",
            item.id,
            wishlist.id,
            request.user.email,
        )
        raise PermissionDenied

    if request.method == "POST":
        form = WishlistItemForm(request.POST, instance=item)

        if form.is_valid():
            item = form.save()

            logger.info(
                "Wishlist item updated: id=%s, title=%s, status=%s, user=%s",
                item.id,
                item.title,
                item.status,
                request.user.email,
            )

            messages.success(request, "Желание обновлено.")
            return redirect("wishlists:wishlist_detail", pk=wishlist.pk)
    else:
        form = WishlistItemForm(instance=item)

    return render(
        request,
        "wishlists/item_form.html",
        {
            "form": form,
            "wishlist": wishlist,
            "item": item,
        },
    )


@login_required
def item_delete_view(request, pk):
    item = get_object_or_404(WishlistItem, pk=pk)
    wishlist = item.wishlist

    if wishlist.owner != request.user:
        logger.warning(
            "Forbidden item delete: item_id=%s, wishlist_id=%s, user=%s",
            item.id,
            wishlist.id,
            request.user.email,
        )
        raise PermissionDenied

    if request.method == "POST":
        logger.warning(
            "Wishlist item deleted: id=%s, title=%s, wishlist_id=%s, user=%s",
            item.id,
            item.title,
            wishlist.id,
            request.user.email,
        )

        item.delete()
        messages.success(request, "Желание удалено.")
        return redirect("wishlists:wishlist_detail", pk=wishlist.pk)

    return render(request, "wishlists/confirm_delete.html", {"object": item})


@login_required
def assign_executor_view(request, pk):
    wishlist = get_object_or_404(Wishlist, pk=pk, owner=request.user)

    if request.method == "POST":
        form = AssignExecutorForm(request.POST, wishlist=wishlist)

        if form.is_valid():
            executor = form.cleaned_data["user"]
            WishlistAccess.objects.create(wishlist=wishlist, user=executor)

            logger.info(
                "Executor assigned: wishlist_id=%s, executor=%s, assigned_by=%s",
                wishlist.id,
                executor.email,
                request.user.email,
            )

            messages.success(request, "Исполнитель назначен.")
        else:
            logger.warning(
                "Failed executor assignment: wishlist_id=%s, user=%s",
                wishlist.id,
                request.user.email,
            )
            messages.error(request, "Не удалось назначить исполнителя.")

    return redirect("wishlists:wishlist_detail", pk=wishlist.pk)


@login_required
def remove_executor_view(request, pk):
    access = get_object_or_404(WishlistAccess, pk=pk)

    if access.wishlist.owner != request.user:
        logger.warning(
            "Forbidden executor removal: wishlist_id=%s, executor=%s, user=%s",
            access.wishlist.id,
            access.user.email,
            request.user.email,
        )
        raise PermissionDenied

    wishlist_pk = access.wishlist.pk

    logger.warning(
        "Executor removed: wishlist_id=%s, executor=%s, removed_by=%s",
        access.wishlist.id,
        access.user.email,
        request.user.email,
    )

    access.delete()
    messages.success(request, "Исполнитель удалён.")

    return redirect("wishlists:wishlist_detail", pk=wishlist_pk)


@login_required
def add_comment_view(request, item_pk):
    item = get_object_or_404(WishlistItem, pk=item_pk)
    wishlist = item.wishlist

    if not user_can_access_wishlist(request.user, wishlist):
        logger.warning(
            "Forbidden comment attempt: item_id=%s, wishlist_id=%s, user=%s",
            item.id,
            wishlist.id,
            request.user.email,
        )
        raise PermissionDenied

    if request.method == "POST":
        form = ItemCommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.item = item
            comment.author = request.user
            comment.save()

            logger.info(
                "Comment added: item_id=%s, author=%s",
                item.id,
                request.user.email,
            )

            messages.success(request, "Комментарий добавлен.")

    return redirect("wishlists:wishlist_detail", pk=wishlist.pk)


@login_required
def export_csv_view(request, pk):
    wishlist = get_object_or_404(Wishlist, pk=pk)

    if not user_can_access_wishlist(request.user, wishlist):
        logger.warning(
            "Forbidden CSV export: wishlist_id=%s, user=%s",
            wishlist.id,
            request.user.email,
        )
        raise PermissionDenied

    logger.info(
        "Wishlist exported to CSV: wishlist_id=%s, user=%s",
        wishlist.id,
        request.user.email,
    )

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="wishlist_{wishlist.pk}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["Название", "Описание", "Ссылка", "Цена", "Приоритет", "Статус"])

    for item in wishlist.items.all():
        writer.writerow(
            [
                item.title,
                item.description,
                item.product_url,
                item.approximate_price or "",
                item.get_priority_display(),
                item.get_status_display(),
            ]
        )

    return response


@login_required
def export_pdf_view(request, pk):
    wishlist = get_object_or_404(Wishlist, pk=pk)

    if not user_can_access_wishlist(request.user, wishlist):
        logger.warning(
            "Forbidden PDF export: wishlist_id=%s, user=%s",
            wishlist.id,
            request.user.email,
        )
        raise PermissionDenied

    logger.info(
        "Wishlist exported to PDF: wishlist_id=%s, user=%s",
        wishlist.id,
        request.user.email,
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="wishlist_{wishlist.pk}.pdf"'

    document = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = [
        Paragraph(f"Wishlist: {wishlist.title}", styles["Title"]),
        Spacer(1, 12),
    ]

    data = [["Название", "Цена", "Приоритет", "Статус"]]

    for item in wishlist.items.all():
        data.append(
            [
                Paragraph(item.title, styles["BodyText"]),
                str(item.approximate_price or ""),
                item.get_priority_display(),
                item.get_status_display(),
            ]
        )

    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )

    elements.append(table)
    document.build(elements)

    return response