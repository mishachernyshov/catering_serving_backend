# Generated by Django 4.1.6 on 2023-06-05 07:06

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('dish', '0004_alter_ordereddish_booking_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dish',
            options={'verbose_name': 'Dish', 'verbose_name_plural': 'Dishes'},
        ),
        migrations.AlterModelOptions(
            name='dishcategory',
            options={'verbose_name': 'Dish category', 'verbose_name_plural': 'Dish categories'},
        ),
        migrations.AlterModelOptions(
            name='dishsubcategory',
            options={'verbose_name': 'Dish subcategory', 'verbose_name_plural': 'Dish subcategories'},
        ),
        migrations.AlterModelOptions(
            name='food',
            options={'verbose_name': 'Food', 'verbose_name_plural': 'Foods'},
        ),
    ]
