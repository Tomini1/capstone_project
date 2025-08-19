from django.contrib import admin

# Register your models here.
from .models import Category, Transaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "user")
    search_fields = ("name", "user__username")
    list_filter = ("user",)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("date", "type", "amount", "user", "category", "description")
    list_filter = ("type", "date", "user", "category")
    search_fields = ("description",)
