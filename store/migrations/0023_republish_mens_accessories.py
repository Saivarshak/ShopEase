from django.db import migrations


def republish_mens_accessories(apps, schema_editor):
    FashionCategory = apps.get_model('store', 'FashionCategory')
    FashionCategory.objects.filter(
        root_category__category_name__iexact='mens',
        slug='mens-accessories',
    ).update(
        is_active=True,
        is_under_maintenance=False,
        page_url='/mens/mens-accessories/',
    )


class Migration(migrations.Migration):
    dependencies = [
        ('store', '0022_normalize_fashion_category_sort_order'),
    ]

    operations = [
        migrations.RunPython(republish_mens_accessories, migrations.RunPython.noop),
    ]
