from pathlib import Path
from datetime import timedelta
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = [x.strip() for x in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if x.strip()]

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "corsheaders", "rest_framework", "rest_framework_simplejwt", "drf_spectacular",
    "accounts", "energy",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{"BACKEND":"django.template.backends.django.DjangoTemplates","DIRS":[],"APP_DIRS":True,"OPTIONS":{"context_processors":["django.template.context_processors.request","django.contrib.auth.context_processors.auth","django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION = "config.wsgi.application"

if os.getenv("POSTGRES_DB"):
    DATABASES={"default":{"ENGINE":"django.db.backends.postgresql","NAME":os.getenv("POSTGRES_DB"),"USER":os.getenv("POSTGRES_USER","postgres"),"PASSWORD":os.getenv("POSTGRES_PASSWORD","postgres"),"HOST":os.getenv("POSTGRES_HOST","db"),"PORT":os.getenv("POSTGRES_PORT","5432")}}
else:
    DATABASES={"default":{"ENGINE":"django.db.backends.sqlite3","NAME":BASE_DIR/"db.sqlite3"}}

AUTH_PASSWORD_VALIDATORS=[]
AUTH_USER_MODEL="accounts.User"
LANGUAGE_CODE="en-au"
TIME_ZONE=os.getenv("DJANGO_TIME_ZONE", "Australia/Adelaide")
USE_I18N=True
USE_TZ=True
STATIC_URL="static/"
STATIC_ROOT=BASE_DIR/"staticfiles"
MEDIA_URL="/media/"
MEDIA_ROOT=BASE_DIR/"media"
DEFAULT_AUTO_FIELD="django.db.models.BigAutoField"

REST_FRAMEWORK={
    "DEFAULT_AUTHENTICATION_CLASSES":("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES":("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS":"drf_spectacular.openapi.AutoSchema",
}
SIMPLE_JWT={"ACCESS_TOKEN_LIFETIME":timedelta(minutes=60),"REFRESH_TOKEN_LIFETIME":timedelta(days=7)}
SPECTACULAR_SETTINGS={"TITLE":"Energy Cost Manager API","DESCRIPTION":"CSV electricity usage analytics and plan comparison API","VERSION":"1.0.0"}

CORS_ALLOWED_ORIGINS=[x.strip() for x in os.getenv("CORS_ALLOWED_ORIGINS","http://localhost:3000").split(",") if x.strip()]
CSRF_TRUSTED_ORIGINS=CORS_ALLOWED_ORIGINS
EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL="noreply@energycostmanager.local"
FRONTEND_URL=os.getenv("FRONTEND_URL","http://localhost:3000")
