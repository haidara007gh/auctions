# Generated by Django 4.1 on 2022-09-07 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0002_alter_listing_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="listing",
            name="url",
            field=models.ImageField(null=True, upload_to="uploads/% Y/% m/% d/"),
        ),
    ]