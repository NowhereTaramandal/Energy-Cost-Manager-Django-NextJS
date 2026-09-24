from django.contrib.auth import get_user_model
from rest_framework import serializers
User=get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=("id","username","first_name","last_name","email","date_joined")
        read_only_fields=("id","date_joined")

class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True, min_length=8)
    confirm_password=serializers.CharField(write_only=True)
    class Meta:
        model=User
        fields=("username","first_name","last_name","email","password","confirm_password")
    def validate(self, attrs):
        if attrs["password"] != attrs.pop("confirm_password"):
            raise serializers.ValidationError({"confirm_password":"Passwords do not match."})
        return attrs
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
