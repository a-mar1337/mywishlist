from django import forms

from accounts.models import User
from .models import ItemComment, Wishlist, WishlistAccess, WishlistItem


class WishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = ("title", "description")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()

        if len(title) < 2:
            raise forms.ValidationError("Название должно содержать минимум 2 символа.")

        return title


class WishlistItemForm(forms.ModelForm):
    class Meta:
        model = WishlistItem
        fields = (
            "title",
            "description",
            "product_url",
            "approximate_price",
            "priority",
            "status",
        )
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "product_url": forms.URLInput(attrs={"class": "form-control"}),
            "approximate_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()

        if len(title) < 2:
            raise forms.ValidationError("Название желания должно содержать минимум 2 символа.")

        return title


class AssignExecutorForm(forms.Form):
    email = forms.EmailField(
        label="Email исполнителя",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "executor@example.com"}),
    )

    def __init__(self, *args, wishlist=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.wishlist = wishlist

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError("Пользователь с таким email не найден.")

        if self.wishlist and self.wishlist.owner == user:
            raise forms.ValidationError("Владелец не может быть исполнителем своего вишлиста.")

        if self.wishlist and WishlistAccess.objects.filter(wishlist=self.wishlist, user=user).exists():
            raise forms.ValidationError("Этот пользователь уже назначен исполнителем.")

        self.cleaned_data["user"] = user
        return email


class ItemCommentForm(forms.ModelForm):
    class Meta:
        model = ItemComment
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean_text(self):
        text = self.cleaned_data.get("text", "").strip()

        if len(text) < 2:
            raise forms.ValidationError("Комментарий должен содержать минимум 2 символа.")

        return text