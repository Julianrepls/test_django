# Generated by Django 5.1.7 on 2025-04-11 11:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0009_alter_author_options_alter_book_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookinstance',
            options={'ordering': ['due_back'], 'permissions': [('can_mark_returned', 'Set book as returned'), ('can_manage_books', 'Can manage book instances')]},
        ),
    ]
