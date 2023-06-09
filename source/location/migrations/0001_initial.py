# Generated by Django 4.1.6 on 2023-05-05 00:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
            options={
                'verbose_name': 'Country',
                'verbose_name_plural': 'Countries',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                (
                    'country',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name='regions', to='location.country'
                    ),
                ),
            ],
            options={
                'verbose_name': 'Region',
                'verbose_name_plural': 'Regions',
            },
        ),
        migrations.CreateModel(
            name='Settlement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                (
                    'region',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name='settlements', to='location.region'
                    ),
                ),
            ],
            options={
                'verbose_name': 'Settlement',
                'verbose_name_plural': 'Settlements',
            },
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                (
                    'settlement',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to='location.settlement'
                    ),
                ),
            ],
            options={
                'verbose_name': 'Address',
                'verbose_name_plural': 'Addresses',
            },
        ),
    ]
