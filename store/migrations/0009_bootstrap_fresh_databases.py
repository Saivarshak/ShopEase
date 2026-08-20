from django.db import migrations


def bootstrap_fresh_databases(apps, schema_editor):
    connection = schema_editor.connection
    existing_tables = set(connection.introspection.table_names())

    Category = apps.get_model('store', 'Category')
    ProductVariant = apps.get_model('store', 'ProductVariant')
    MenCategory = apps.get_model('store', 'MenCategory')
    WomenCategory = apps.get_model('store', 'WomenCategory')
    KidsCategory = apps.get_model('store', 'KidsCategory')
    SiteAsset = apps.get_model('store', 'SiteAsset')
    PageAsset = apps.get_model('store', 'PageAsset')
    HomeContent = apps.get_model('store', 'HomeContent')

    for model in (MenCategory, WomenCategory, KidsCategory, SiteAsset, PageAsset, HomeContent):
        if model._meta.db_table not in existing_tables:
            schema_editor.create_model(model)
            existing_tables.add(model._meta.db_table)

    if ProductVariant._meta.db_table in existing_tables:
        with connection.cursor() as cursor:
            existing_columns = {
                column.name
                for column in connection.introspection.get_table_description(
                    cursor,
                    ProductVariant._meta.db_table,
                )
            }

        for field_name in ('image1', 'image2', 'image3', 'image4'):
            field = ProductVariant._meta.get_field(field_name)
            if field.column not in existing_columns:
                schema_editor.add_field(ProductVariant, field)
                existing_columns.add(field.column)


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_order_razorpay_fields'),
    ]

    operations = [
        migrations.RunPython(bootstrap_fresh_databases, migrations.RunPython.noop),
    ]
