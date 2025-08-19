from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Category, Transaction

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "first_name", "last_name"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "user"]
        read_only_fields = ["user"]

class TransactionSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source="category", read_only=True)

    class Meta:
        model = Transaction
        fields = ["id", "user", "category", "category_detail", "amount", "type", "description", "date", "created_at"]
        read_only_fields = ["user", "created_at"]

    def validate(self, attrs):
        amount = attrs.get("amount")
        if amount is None or amount <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        ttype = attrs.get("type")
        if ttype not in ("INCOME", "EXPENSE"):
            raise serializers.ValidationError("Invalid type. Use INCOME or EXPENSE.")
        return attrs
