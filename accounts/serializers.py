from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser
from .services import generate_otp, verify_otp

class RegisterSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    phone    = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("E-mail already in use")
        return value

    def create(self, validated):
        user = CustomUser.objects.create_user(
            email=validated["email"],
            phone=validated["phone"],
            password=validated["password"],
        )
        generate_otp(user.phone)
        return user

class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField()
    otp   = serializers.CharField(max_length=6)

    def validate(self, data):
        if not verify_otp(data["phone"], data["otp"]):
            raise serializers.ValidationError("Invalid / expired OTP")
        return data

class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if not user:
            raise serializers.ValidationError("Incorrect credentials")
        data["user"] = user
        return data

class ResendOTPSerializer(serializers.Serializer):
    phone = serializers.CharField()

    def validate_phone(self, value):
        try:
            user = CustomUser.objects.get(phone=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("No account with this phone")

        if user.is_verified:
            raise serializers.ValidationError("Account already verified")
        self.user = user                  
        return value
