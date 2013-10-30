from django.db import models
from django.contrib.auth.models import User

from django_localflavor_us.models import USStateField


class Contact(models.Model):
    name = models.CharField(max_length=128)


class Agent(models.Model):
    user = models.OneToOneField(User)
    contact = models.ForeignKey(Contact)


class Property(models.Model):
    contact = models.ForeignKey(Agent)
    address_one = models.CharField(max_length=128)
    address_two = models.CharField(max_length=128, null=True, blank=True)
    city = models.CharField(max_length=128)
    state = USStateField()
    # TODO: figure out how to hook up the
    # django_localflavor_us.forms.USZipCodeField form field
    # (for validation).
    zipcode = models.CharField(max_length=11)


class Rooms(models.Model):
    property = models.OneToOneField(Property)
    bed = models.PositiveSmallIntegerField(default=0)
    bath = models.PositiveSmallIntegerField(default=0)
    living = models.BooleanField()
    family = models.BooleanField()
    dining = models.BooleanField()
    eatin = models.BooleanField()
    bonus = models.BooleanField()
    loft = models.BooleanField()


class Amenities(models.Model):
    property = models.OneToOneField(Property)
    gasfire = models.BooleanField()
    woodfire = models.BooleanField()
    year = models.PositiveSmallIntegerField()


class Rental(Property):
    rent = models.DecimalField(decimal_places=2, max_digits=7)
    deposit = models.DecimalField(decimal_places=2, max_digits=7)


class Listing(Property):
    price = models.DecimalField(decimal_places=2, max_digits=10)
