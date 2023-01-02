from django.contrib import admin
from .models import *

class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title","user","price","category")

# Register your models here.

admin.site.register(Listing, ListingAdmin)
admin.site.register(Comment)
admin.site.register(Bid)