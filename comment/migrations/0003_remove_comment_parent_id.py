# Generated by Django 4.1.7 on 2023-03-25 09:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comment', '0002_alter_comment_options_comment_parent_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='parent_id',
        ),
    ]