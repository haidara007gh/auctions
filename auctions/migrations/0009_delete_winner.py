# Generated by Django 4.1 on 2022-10-13 16:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0008_alter_bid_listing_winner"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Winner",
        ),
    ]