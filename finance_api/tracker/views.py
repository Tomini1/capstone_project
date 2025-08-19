from django.shortcuts import render

# Create your views here.
from datetime import date
from calendar import monthrange
from decimal import Decimal
from django.contrib.auth.models import User
from django.db.models import Sum, F
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Transaction
from .serializers import UserSerializer, CategorySerializer, TransactionSerializer
from .permissions import IsOwnerOrAdmin

# Users: Create (open), detail/update/delete (owner/admin)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        if self.action in ("retrieve", "update", "partial_update", "destroy"):
            return [IsAuthenticated()]
        # List restricted to admin to avoid leaking users
        if self.action == "list":
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_object(self):
        obj = super().get_object()
        # Enforce owner/admin at object level
        if not (self.request.user.is_staff or obj.id == self.request.user.id):
            self.permission_denied(self.request, message="Not allowed.")
        return obj

# Categories: scoped to request.user
class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user).order_by("name")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj

    def check_object_permissions(self, request, obj):
        if not (request.user.is_staff or obj.user_id == request.user.id):
            self.permission_denied(request, message="Not allowed.")

# Transactions: scoped to request.user
class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        qs = Transaction.objects.select_related("category").filter(user=self.request.user)
        # Optional filters: month, year, type, category
        month = self.request.query_params.get("month")
        year = self.request.query_params.get("year")
        ttype = self.request.query_params.get("type")
        category = self.request.query_params.get("category")
        if year and month:
            qs = qs.filter(date__year=int(year), date__month=int(month))
        if ttype:
            qs = qs.filter(type=ttype)
        if category:
            qs = qs.filter(category_id=category)
        return qs.order_by("-date", "-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_object(self):
        obj = super().get_object()
        if not (self.request.user.is_staff or obj.user_id == self.request.user.id):
            self.permission_denied(self.request, message="Not allowed.")
        return obj

# Reports
class MonthlySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month = request.query_params.get("month")
        year = request.query_params.get("year")
        if not (month and year):
            return Response({"detail": "Provide month=MM and year=YYYY"}, status=400)
        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return Response({"detail": "Invalid month/year"}, status=400)

        qs = Transaction.objects.filter(user=request.user, date__year=year, date__month=month)
        income = qs.filter(type="INCOME").aggregate(total=Sum("amount"))["total"] or Decimal("0")
        expense = qs.filter(type="EXPENSE").aggregate(total=Sum("amount"))["total"] or Decimal("0")
        net = income - expense
        return Response({
            "month": f"{year:04d}-{month:02d}",
            "income": str(income),
            "expense": str(expense),
            "net": str(net),
        })

class CategoryBreakdownView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month = request.query_params.get("month")
        year = request.query_params.get("year")
        if not (month and year):
            return Response({"detail": "Provide month=MM and year=YYYY"}, status=400)
        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return Response({"detail": "Invalid month/year"}, status=400)

        qs = (
            Transaction.objects.filter(user=request.user, type="EXPENSE", date__year=year, date__month=month)
            .values(name=F("category__name"))
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )
        # Convert Decimals to strings for JSON safety
        data = [{"category": row["name"] or "Uncategorized", "total": str(row["total"])} for row in qs]
        return Response({"month": f"{year:04d}-{month:02d}", "items": data})
