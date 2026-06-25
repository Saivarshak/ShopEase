# Compatibility migration kept so deployments that have seen 0017 keep a stable graph.
# The tables referenced here are already represented in 0005_reconcile_state.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_hide_nonrequired_main_categories'),
    ]

    operations = []