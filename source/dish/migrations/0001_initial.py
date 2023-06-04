# Generated by Django 4.1.6 on 2023-05-05 00:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('catering_establishment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CateringEstablishmentDish',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('photo', models.ImageField(upload_to='dish/photos/')),
                ('price', models.FloatField()),
                (
                    'catering_establishment',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='catering_establishment_dishes',
                        to='catering_establishment.cateringestablishment',
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='DishCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'booking',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to='catering_establishment.booking'
                    ),
                ),
                ('dishes', models.ManyToManyField(related_name='orders', to='dish.cateringestablishmentdish')),
            ],
        ),
        migrations.CreateModel(
            name='DishSubcategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                (
                    'category',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='subcategories',
                        to='dish.dishcategory',
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='Dish',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('food', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dish.food')),
                (
                    'subcategory',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name='dishes', to='dish.dishsubcategory'
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField()),
                (
                    'type',
                    models.CharField(choices=[('percent', 'Percent'), ('cash_value', 'Cash value')], max_length=16),
                ),
                ('amount', models.FloatField()),
                (
                    'catering_establishment_dish',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to='dish.cateringestablishmentdish'
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='cateringestablishmentdish',
            name='dish',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='catering_establishment_dishes',
                to='dish.dish',
            ),
        ),
    ]