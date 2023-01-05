# Generated by Django 4.1.1 on 2022-12-13 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_alter_userstatus_user_authorrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='status',
            field=models.CharField(
                choices=[('PUBLISHED', 'Published'), ('DRAFT', 'Draft')], default='PUBLISHED', max_length=20
            ),
        ),
        migrations.AlterField(
            model_name='post',
            name='status',
            field=models.CharField(
                choices=[('PUBLISHED', 'Published'), ('DRAFT', 'Draft')], default='DRAFT', max_length=20
            ),
        ),
    ]
