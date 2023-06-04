# Generated by Django 4.1.6 on 2023-05-26 06:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('catering_establishment', '0003_workhours_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cateringestablishment',
            name='work_hours',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='catering_establishment',
                to='catering_establishment.workhours',
            ),
        ),
    ]
