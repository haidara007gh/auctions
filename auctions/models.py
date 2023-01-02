from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listed_items")
    active = models.BooleanField(verbose_name="status")
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=64)
    datetime = models.DateTimeField()
    url = models.ImageField(upload_to ='images/', null=True)
    price = models.FloatField()
    category = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.title}: Price:{self.price} Active: {self.active}"

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bidded_on")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.FloatField()
    datetime= models.DateTimeField(verbose_name="when bidding was made")

    def __str__(self):
        return f"Price: {self.price}"   

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    message = models.TextField(max_length=128)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime= models.DateTimeField(verbose_name="when comment was made")

    def __str__(self):
        return f"Message: {self.message}"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.listing}"
    
class Winner(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user}"