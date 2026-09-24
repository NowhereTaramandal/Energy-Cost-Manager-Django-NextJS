from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer, UserSerializer

User=get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset=User.objects.all(); serializer_class=RegisterSerializer; permission_classes=[permissions.AllowAny]

class MeView(generics.RetrieveUpdateAPIView):
    serializer_class=UserSerializer
    def get_object(self): return self.request.user

class ForgotPasswordView(APIView):
    permission_classes=[permissions.AllowAny]
    def post(self, request):
        email=request.data.get("email", "").strip().lower()
        user=User.objects.filter(email__iexact=email).first()
        if user:
            uid=urlsafe_base64_encode(force_bytes(user.pk))
            token=default_token_generator.make_token(user)
            link=f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"
            send_mail("Reset your Energy Cost Manager password", f"Reset your password: {link}", settings.DEFAULT_FROM_EMAIL, [user.email])
        return Response({"detail":"If the email exists, a reset link has been sent."})

class ResetPasswordView(APIView):
    permission_classes=[permissions.AllowAny]
    def post(self, request):
        try:
            uid=force_str(urlsafe_base64_decode(request.data.get("uid", "")))
            user=User.objects.get(pk=uid)
        except Exception:
            return Response({"detail":"Invalid reset link."}, status=400)
        token=request.data.get("token", ""); password=request.data.get("password", "")
        if len(password) < 8 or not default_token_generator.check_token(user, token):
            return Response({"detail":"Invalid token or password too short."}, status=400)
        user.set_password(password); user.save(update_fields=["password"])
        return Response({"detail":"Password reset successfully."})
