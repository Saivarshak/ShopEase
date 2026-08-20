from django.db import migrations, models
import django.db.models.deletion

def create_missing_tables(apps, schema_editor):
    connection = schema_editor.connection
    existing_tables = set(connection.introspection.table_names())
    
    # Models to ensure tables exist for
    models_to_check = [
        ('store', 'MenCategory', 'men_categories'),
        ('store', 'WomenCategory', 'women_categories'),
        ('store', 'KidsCategory', 'kids_categories'),
        ('store', 'SiteAsset', 'site_assets'),
        ('store', 'PageAsset', 'page_assets'),
        ('store', 'HomeContent', 'home_content'),
    ]
    
    for app_label, model_name, table_name in models_to_check:
        if table_name not in existing_tables:
            model = apps.get_model(app_label, model_name)
            schema_editor.create_model(model)
            existing_tables.add(table_name)

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0019_alter_homecontent_options_alter_kidscategory_options_and_more'),
    ]

    operations = [
        migrations.RunPython(create_missing_tables, migrations.RunPython.noop),
    ]
