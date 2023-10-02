# Generated by Django 4.2.5 on 2023-10-02 12:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=255)),
                ('video_data', models.BinaryField(blank=True, null=True)),
                ('video_file_path', models.URLField(blank=True, null=True)),
                ('completed', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('transcript', models.TextField(blank=True, null=True)),
                ('transcript_path', models.URLField(blank=True, null=True)),
                ('transcript_data', models.BinaryField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='VideoChunk',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chunk_data_path', models.CharField(max_length=255)),
                ('chunk_index', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='video_chunks', to='videos.video')),
            ],
        ),
    ]