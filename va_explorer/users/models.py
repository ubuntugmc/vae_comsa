from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _

# from allauth.account.models import EmailAddress
# from allauth.account.signals import email_confirmed
# from django.dispatch import receiver
from va_explorer.va_data_management.models import Location


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of username.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_("Email is required"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.original_password = self.password

    email = models.EmailField(_("email address"), unique=True)
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    has_valid_password = models.BooleanField(
        _("The user has a user-defined password"), default=False
    )

    locations = models.ManyToManyField(Location, related_name="users")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.pk})

    # TODO: Remove if we do not require email confirmation; we will no longer need the lines below
    # def add_email_address(self, request, new_email):
    #     return EmailAddress.objects.add_email(request, self.user, new_email, confirm=True)
    #
    # @receiver(email_confirmed)
    # def update_user_email(sender, email_address, **kwargs):
    #     email_address.set_as_primary()
    #
    #     EmailAddress.objects.filter(
    #         user=email_address.user).exclude(primary=True).delete()

    def save(self, *args, **kwargs):
        # TODO: May need to be changed depending on how username comes in from ODK?
        self.username = self.email
        super(User, self).save(*args, **kwargs)
        if self.original_password != self.password:
            UserPasswordHistory.remember_password(self)


class UserPasswordHistory(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    old_password = models.CharField(max_length=128)
    password_date = models.DateTimeField()

    @classmethod
    def remember_password(cls, user):
        cls(username=user, old_password=user.password, password_date=localtime()).save()
