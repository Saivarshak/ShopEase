import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

import django
from django.apps import apps
from django.db import models
from django.db.models import NOT_PROVIDED


BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shopease.settings")
django.setup()

from store.models import _calculate_offer_price

STRING_FIELDS = (
    models.CharField,
    models.TextField,
    models.EmailField,
    models.SlugField,
    models.URLField,
)
NUMERIC_FIELDS = (
    models.IntegerField,
    models.PositiveIntegerField,
    models.PositiveSmallIntegerField,
    models.SmallIntegerField,
    models.BigIntegerField,
    models.FloatField,
    models.DecimalField,
)


def replacement_for_field(field):
    if field.default is not NOT_PROVIDED:
        default_value = field.get_default()
        return default_value() if callable(default_value) else default_value

    if isinstance(field, STRING_FIELDS):
        return ""

    if isinstance(field, models.BooleanField):
        return False

    if isinstance(field, NUMERIC_FIELDS):
        return 0

    return NOT_PROVIDED


def sanitize_fixture(input_path, output_path):
    records = json.loads(Path(input_path).read_text(encoding="utf-8"))
    changes = Counter()
    skipped = []

    for record in records:
        model_label = record.get("model")
        fields = record.get("fields", {})

        try:
            app_label, model_name = model_label.split(".", 1)
            model = apps.get_model(app_label, model_name)
        except Exception:
            skipped.append(model_label)
            continue

        for field in model._meta.local_fields:
            if field.auto_created or field.primary_key:
                continue

            field_name = field.name
            if model_label == "store.product" and field_name == "offer_price":
                if field_name not in fields or fields[field_name] is None:
                    fields[field_name] = str(
                        _calculate_offer_price(
                            fields.get("price"),
                            fields.get("discount_percent"),
                        )
                    )
                    changes[f"{model_label}.{field_name}"] += 1
                continue

            if field_name not in fields:
                if field.null:
                    continue

                replacement = replacement_for_field(field)
                if replacement is NOT_PROVIDED:
                    continue

                fields[field_name] = replacement
                changes[f"{model_label}.{field_name}"] += 1
                continue

            if fields[field_name] is not None or field.null:
                continue

            replacement = replacement_for_field(field)
            if replacement is NOT_PROVIDED:
                continue

            fields[field_name] = replacement
            changes[f"{model_label}.{field_name}"] += 1

    Path(output_path).write_text(json.dumps(records, indent=2), encoding="utf-8")

    print(f"Wrote sanitized fixture to {output_path}")
    if changes:
        for key, count in sorted(changes.items()):
            print(f"{key}: {count}")
    else:
        print("No changes were required.")

    if skipped:
        print("Skipped unresolved models:")
        for model_label in sorted(set(skipped)):
            print(f"- {model_label}")


def main():
    parser = argparse.ArgumentParser(description="Sanitize Django fixture data for stricter database backends.")
    parser.add_argument("input_path", help="Path to the source fixture JSON file")
    parser.add_argument("output_path", help="Path to write the sanitized fixture JSON file")
    args = parser.parse_args()
    sanitize_fixture(args.input_path, args.output_path)


if __name__ == "__main__":
    main()
