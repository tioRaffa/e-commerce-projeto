# Generated by Django 5.2.3 on 2025-07-07 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_alter_bookmodel_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookmodel',
            name='publisher',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Editora'),
        ),
    ]
