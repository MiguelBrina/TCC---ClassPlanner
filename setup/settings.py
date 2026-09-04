from pathlib import Path
import os


# ============================================================
# CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# URL DO AMBIENTE
# ============================================================

SITE_URL = SITE_URL = "https://potential-space-waffle-x5x4qqxrv4g5cv4wr-8000.app.github.dev"


# ============================================================
# SEGURANÇA BÁSICA
# ============================================================

SECRET_KEY = 'django-insecure-)%nm&!q2*xs_)8euokjzs)wah(6fl8-pol=t3j@_ku__8*ryd8'

DEBUG = True


ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".app.github.dev",
]


CSRF_TRUSTED_ORIGINS = [
    SITE_URL,
    "http://localhost:8000",
    "https://localhost:8000",
]


# O Codespaces fica atrás de um proxy HTTPS.
# Essas configurações fazem o Django respeitar
# o protocolo e o host originais da requisição.
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

USE_X_FORWARDED_HOST = True

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "EMAIL_AUTHENTICATION": True,
        "EMAIL_AUTHENTICATION_AUTO_CONNECT": True,
    },
}

# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # Apps do ClassPlanner
    "core",
    "account.apps.AccountConfig",

    # django-allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "allauth.account.middleware.AccountMiddleware",
]


# ============================================================
# AUTENTICAÇÃO
# ============================================================

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]


# ============================================================
# DJANGO SITES
# ============================================================

SITE_ID = 1


# ============================================================
# CONFIGURAÇÕES DA CONTA
# ============================================================

ACCOUNT_LOGIN_METHODS = {"email"}

ACCOUNT_SIGNUP_FIELDS = [
    "email*",
    "password1*",
    "password2*",
]

ACCOUNT_SIGNUP_FORM_CLASS = "account.forms.FormularioCadastro"

ACCOUNT_EMAIL_VERIFICATION = "mandatory"


# Redirecionamentos
LOGIN_REDIRECT_URL = "/pos-login/"
LOGOUT_REDIRECT_URL = "/"


# ============================================================
# E-MAIL
# ============================================================

# Desenvolvimento:
# imprime os e-mails no terminal do Codespace/local.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# ============================================================
# URLS
# ============================================================

ROOT_URLCONF = "setup.urls"


# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "setup.wsgi.application"


# ============================================================
# BANCO DE DADOS
# ============================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ============================================================
# VALIDAÇÃO DE SENHAS
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 10,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "account.password_validators.ValidadorSenhaForte",
    },
]


# ============================================================
# INTERNACIONALIZAÇÃO
# ============================================================

LANGUAGE_CODE = "pt-br"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# ============================================================
# ARQUIVOS ESTÁTICOS
# ============================================================


STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

