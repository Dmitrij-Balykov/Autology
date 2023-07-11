# Generated by Django 3.2.11 on 2022-05-25 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='upload_file',
            name='file_owner',
        ),
        migrations.AddField(
            model_name='upload_file',
            name='uploaded_file',
            field=models.FileField(default=1, upload_to='Uploaded Files/'),
            preserve_default=False,
        ),
    ]