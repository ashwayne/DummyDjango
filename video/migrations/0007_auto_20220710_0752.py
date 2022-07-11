# Generated by Django 3.2 on 2022-07-10 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0006_tileimage_parent_ortho'),
    ]

    operations = [
        migrations.AddField(
            model_name='orthoimage',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='orthoimage',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]