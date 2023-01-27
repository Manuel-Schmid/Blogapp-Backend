# Generated by Django 4.1.1 on 2023-01-26 08:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_postrelation'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dark_theme_active', models.BooleanField(default=False)),
                ('comment_section_collapsed', models.BooleanField(default=False)),
                ('related_posts_collapsed', models.BooleanField(default=False)),
                ('language', models.CharField(choices=[('ENGLISH', 'En'), ('GERMAN', 'De')], default='ENGLISH', max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]