# Generated by Django 4.1.1 on 2023-01-18 07:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_post_date_updated_alter_post_date_created'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_main_posts', to=settings.AUTH_USER_MODEL)),
                ('main_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_main_posts', to='blog.post')),
                ('sub_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_sub_posts', to='blog.post')),
            ],
            options={
                'unique_together': {('main_post', 'sub_post')},
            },
        ),
    ]
