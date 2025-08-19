from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CategoryViewSet, TransactionViewSet, MonthlySummaryView, CategoryBreakdownView

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"transactions", TransactionViewSet, basename="transaction")

urlpatterns = [
    path("", include(router.urls)),
    path("reports/monthly-summary/", MonthlySummaryView.as_view(), name="monthly-summary"),
    path("reports/category-breakdown/", CategoryBreakdownView.as_view(), name="category-breakdown"),
]
