# Generated manually to align migration state with the existing database schema.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_cartitem_persistent'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name='MenCategory',
                    fields=[
                        ('men_category_id', models.AutoField(primary_key=True, serialize=False)),
                        ('category_name', models.CharField(max_length=100)),
                        ('image', models.CharField(blank=True, max_length=255, null=True)),
                        ('description', models.TextField(blank=True, null=True)),
                        ('page_url', models.CharField(blank=True, max_length=255, null=True)),
                        ('is_active', models.BooleanField(default=True)),
                        ('created_at', models.DateTimeField(blank=True, null=True)),
                        ('category', models.ForeignKey(db_column='category_id', on_delete=django.db.models.deletion.CASCADE, to='store.category')),
                    ],
                    options={
                        'db_table': 'men_categories',
                        'managed': False,
                    },
                ),
                migrations.CreateModel(
                    name='WomenCategory',
                    fields=[
                        ('women_category_id', models.AutoField(primary_key=True, serialize=False)),
                        ('category_name', models.CharField(max_length=100)),
                        ('image', models.CharField(blank=True, max_length=255, null=True)),
                        ('description', models.TextField(blank=True, null=True)),
                        ('page_url', models.CharField(blank=True, max_length=255, null=True)),
                        ('is_active', models.BooleanField(default=True)),
                        ('created_at', models.DateTimeField(blank=True, null=True)),
                        ('category', models.ForeignKey(db_column='category_id', on_delete=django.db.models.deletion.CASCADE, to='store.category')),
                    ],
                    options={
                        'db_table': 'women_categories',
                        'managed': False,
                    },
                ),
                migrations.CreateModel(
                    name='KidsCategory',
                    fields=[
                        ('kids_category_id', models.AutoField(primary_key=True, serialize=False)),
                        ('category_name', models.CharField(max_length=100)),
                        ('image', models.CharField(blank=True, max_length=255, null=True)),
                        ('description', models.TextField(blank=True, null=True)),
                        ('page_url', models.CharField(blank=True, max_length=255, null=True)),
                        ('is_active', models.BooleanField(default=True)),
                        ('created_at', models.DateTimeField(blank=True, null=True)),
                        ('category', models.ForeignKey(db_column='category_id', on_delete=django.db.models.deletion.CASCADE, to='store.category')),
                    ],
                    options={
                        'db_table': 'kids_categories',
                        'managed': False,
                    },
                ),
                migrations.CreateModel(
                    name='SiteAsset',
                    fields=[
                        ('asset_id', models.AutoField(primary_key=True, serialize=False)),
                        ('asset_key', models.CharField(max_length=100, unique=True)),
                        ('image_path', models.CharField(max_length=255)),
                        ('is_active', models.BooleanField(default=True)),
                    ],
                    options={
                        'db_table': 'site_assets',
                        'managed': False,
                    },
                ),
                migrations.CreateModel(
                    name='PageAsset',
                    fields=[
                        ('page_asset_id', models.AutoField(primary_key=True, serialize=False)),
                        ('page_key', models.CharField(max_length=100)),
                        ('asset_key', models.CharField(max_length=100)),
                        ('image_path', models.CharField(max_length=255)),
                        ('is_active', models.BooleanField(default=True)),
                    ],
                    options={
                        'db_table': 'page_assets',
                        'managed': False,
                    },
                ),
                migrations.CreateModel(
                    name='HomeContent',
                    fields=[
                        ('home_content_id', models.AutoField(primary_key=True, serialize=False)),
                        ('hero_subtitle', models.CharField(blank=True, max_length=255, null=True)),
                        ('hero_title', models.CharField(blank=True, max_length=255, null=True)),
                        ('hero_highlight', models.CharField(blank=True, max_length=255, null=True)),
                        ('hero_tagline', models.CharField(blank=True, max_length=255, null=True)),
                        ('hero_button_text', models.CharField(blank=True, max_length=100, null=True)),
                        ('hero_button_url', models.CharField(blank=True, max_length=255, null=True)),
                        ('search_placeholder', models.CharField(blank=True, max_length=255, null=True)),
                        ('search_button_text', models.CharField(blank=True, max_length=100, null=True)),
                        ('nav_home_text', models.CharField(blank=True, max_length=100, null=True)),
                        ('nav_home_url', models.CharField(blank=True, max_length=255, null=True)),
                        ('nav_products_text', models.CharField(blank=True, max_length=100, null=True)),
                        ('nav_products_url', models.CharField(blank=True, max_length=255, null=True)),
                        ('nav_contact_text', models.CharField(blank=True, max_length=100, null=True)),
                        ('nav_contact_url', models.CharField(blank=True, max_length=255, null=True)),
                        ('nav_login_text', models.CharField(blank=True, max_length=100, null=True)),
                        ('nav_login_url', models.CharField(blank=True, max_length=255, null=True)),
                        ('category_section_title', models.CharField(blank=True, max_length=255, null=True)),
                        ('men_description', models.CharField(blank=True, max_length=255, null=True)),
                        ('women_description', models.CharField(blank=True, max_length=255, null=True)),
                        ('kids_description', models.CharField(blank=True, max_length=255, null=True)),
                        ('featured_section_title', models.CharField(blank=True, max_length=255, null=True)),
                        ('footer_text', models.CharField(blank=True, max_length=255, null=True)),
                        ('footer_brand_text', models.CharField(blank=True, max_length=100, null=True)),
                        ('footer_builder_text', models.CharField(blank=True, max_length=100, null=True)),
                        ('is_active', models.BooleanField(default=True)),
                    ],
                    options={
                        'db_table': 'home_content',
                        'managed': False,
                    },
                ),
                migrations.AddField(
                    model_name='productvariant',
                    name='image1',
                    field=models.CharField(blank=True, max_length=255, null=True),
                ),
                migrations.AddField(
                    model_name='productvariant',
                    name='image2',
                    field=models.CharField(blank=True, max_length=255, null=True),
                ),
                migrations.AddField(
                    model_name='productvariant',
                    name='image3',
                    field=models.CharField(blank=True, max_length=255, null=True),
                ),
                migrations.AddField(
                    model_name='productvariant',
                    name='image4',
                    field=models.CharField(blank=True, max_length=255, null=True),
                ),
            ],
        ),
    ]
