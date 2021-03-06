# Generated by Django 2.1.3 on 2018-12-10 15:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20181210_1212'),
    ]

    operations = [
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_picture_name', models.TextField(blank=True, null=True)),
                ('profile_picture_url', models.TextField(blank=True, null=True)),
                ('profile_picture_key', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='Deleted at')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='profile',
            name='profile_picture_key',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='profile_picture_name',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='profile_picture_url',
        ),
        migrations.AddField(
            model_name='profile',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='upload',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='profile_picture', to='user.Profile', verbose_name='profile_uploader'),
        ),
    ]
