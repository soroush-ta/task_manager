# Generated by Django 5.1.3 on 2024-11-13 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='signup_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
