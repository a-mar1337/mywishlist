from django.urls import path

from . import views


app_name = "wishlists"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("create/", views.wishlist_create_view, name="wishlist_create"),
    path("<int:pk>/", views.wishlist_detail_view, name="wishlist_detail"),
    path("<int:pk>/edit/", views.wishlist_update_view, name="wishlist_update"),
    path("<int:pk>/delete/", views.wishlist_delete_view, name="wishlist_delete"),
    path("<int:wishlist_pk>/items/create/", views.item_create_view, name="item_create"),
    path("items/<int:pk>/edit/", views.item_update_view, name="item_update"),
    path("items/<int:pk>/delete/", views.item_delete_view, name="item_delete"),
    path("<int:pk>/assign/", views.assign_executor_view, name="assign_executor"),
    path("access/<int:pk>/delete/", views.remove_executor_view, name="remove_executor"),
    path("items/<int:item_pk>/comments/add/", views.add_comment_view, name="add_comment"),
    path("<int:pk>/export/csv/", views.export_csv_view, name="export_csv"),
    path("<int:pk>/export/pdf/", views.export_pdf_view, name="export_pdf"),
]