# Generated by Django 3.2 on 2022-05-22 11:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0002_auto_20220522_1146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orthoimage',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='video.customer'),
        ),
        migrations.AlterField(
            model_name='orthoimage',
            name='image_type',
            field=models.CharField(blank=True, choices=[(0, 'rgb'), (1, 'multi-spectral'), (2, 'hyper-spectral')], max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='orthoimage',
            name='image_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
