import django_filters
from .models import Transaction


class TransactionFilter(django_filters.FilterSet):
    min_date = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    max_date = django_filters.DateFilter(field_name="date", lookup_expr="lte")
    min_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    max_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")
    type = django_filters.CharFilter(field_name="type")
    category = django_filters.NumberFilter(field_name="category_id")
    account = django_filters.NumberFilter(field_name="account_id")
    tags = django_filters.CharFilter(field_name="tags", lookup_expr="icontains")

    class Meta:
        model = Transaction
        fields = ["type", "category", "account", "min_date", "max_date", "min_amount", "max_amount", "tags"]
