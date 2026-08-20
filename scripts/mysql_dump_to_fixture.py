import json
import re
import sys
from pathlib import Path

import django


RELEVANT_TABLES = {
    "auth_user": "auth.user",
    "categories": "store.category",
    "subcategories": "store.subcategory",
    "men_categories": "store.mencategory",
    "women_categories": "store.womencategory",
    "kids_categories": "store.kidscategory",
    "site_assets": "store.siteasset",
    "page_assets": "store.pageasset",
    "home_content": "store.homecontent",
    "products": "store.product",
    "product_variants": "store.productvariant",
    "cart_items": "store.cartitem",
    "orders": "store.order",
    "order_items": "store.orderitem",
}


def parse_create_table_columns(sql_text):
    pattern = re.compile(
        r"CREATE TABLE `(?P<table>[^`]+)` \((?P<body>.*?)\)\s*ENGINE=",
        re.S,
    )
    columns = {}
    for match in pattern.finditer(sql_text):
        table = match.group("table")
        if table not in RELEVANT_TABLES:
            continue
        body = match.group("body")
        table_columns = []
        for line in body.splitlines():
            stripped = line.strip()
            if stripped.startswith("`"):
                table_columns.append(stripped.split("`", 2)[1])
        columns[table] = table_columns
    return columns


def parse_rows(values_blob):
    rows = []
    i = 0
    n = len(values_blob)
    while i < n:
        while i < n and values_blob[i] in " \r\n\t,":
            i += 1
        if i >= n:
            break
        if values_blob[i] != "(":
            raise ValueError(f"Expected '(' at position {i}")
        i += 1
        row = []
        token = []
        in_string = False
        while i < n:
            ch = values_blob[i]
            if in_string:
                if ch == "\\":
                    i += 1
                    if i >= n:
                        break
                    escaped = values_blob[i]
                    escape_map = {
                        "0": "\0",
                        "b": "\b",
                        "n": "\n",
                        "r": "\r",
                        "t": "\t",
                        "Z": "\x1a",
                        "\\": "\\",
                        "'": "'",
                        '"': '"',
                    }
                    token.append(escape_map.get(escaped, escaped))
                elif ch == "'":
                    in_string = False
                else:
                    token.append(ch)
            else:
                if ch == "'":
                    in_string = True
                elif ch == ",":
                    row.append("".join(token).strip())
                    token = []
                elif ch == ")":
                    row.append("".join(token).strip())
                    token = []
                    rows.append(row)
                    i += 1
                    break
                else:
                    token.append(ch)
            i += 1
    return rows


def convert_raw_value(raw):
    if raw == "NULL" or raw == "":
        return None
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    if re.fullmatch(r"-?\d+\.\d+", raw):
        return raw
    return raw


def build_field_maps():
    django.setup()
    from django.apps import apps

    model_map = {}
    for table, label in RELEVANT_TABLES.items():
        model = apps.get_model(label)
        model_map[table] = model
    return model_map


def coerce_for_field(field, value):
    if value is None:
        return None
    internal_type = field.get_internal_type()
    if internal_type in {"BooleanField", "NullBooleanField"}:
        return bool(int(value))
    if internal_type in {
        "AutoField",
        "BigAutoField",
        "IntegerField",
        "BigIntegerField",
        "PositiveIntegerField",
        "PositiveSmallIntegerField",
        "SmallIntegerField",
    }:
        return int(value)
    if internal_type == "DecimalField":
        return str(value)
    if internal_type in {"DateTimeField", "DateField", "TimeField"}:
        return str(value)
    if field.is_relation:
        return int(value)
    return value


def build_fixture(sql_text):
    columns_by_table = parse_create_table_columns(sql_text)
    model_map = build_field_maps()
    insert_pattern = re.compile(
        r"INSERT INTO `(?P<table>[^`]+)`(?: \((?P<columns>.*?)\))? VALUES (?P<values>.*?);",
        re.S,
    )

    fixture = []
    for match in insert_pattern.finditer(sql_text):
        table = match.group("table")
        if table not in RELEVANT_TABLES:
            continue
        rows = parse_rows(match.group("values"))
        explicit_columns = match.group("columns")
        if explicit_columns:
            columns = re.findall(r"`([^`]+)`", explicit_columns)
        else:
            columns = columns_by_table[table]
        model = model_map[table]
        field_by_column = {field.column: field for field in model._meta.local_fields}
        pk_field = model._meta.pk

        for row in rows:
            obj = {"model": model._meta.label_lower, "pk": None, "fields": {}}
            for column_name, raw in zip(columns, row):
                field = field_by_column.get(column_name)
                if field is None:
                    continue
                value = coerce_for_field(field, convert_raw_value(raw))
                if field == pk_field:
                    obj["pk"] = value
                else:
                    obj["fields"][field.name] = value
            if obj["pk"] is not None:
                fixture.append(obj)
    return fixture


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python scripts/mysql_dump_to_fixture.py <input.sql> <output.json>")

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    sql_text = input_path.read_text(encoding="utf-8")
    fixture = build_fixture(sql_text)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(fixture, indent=2), encoding="utf-8")
    print(f"Wrote {len(fixture)} fixture objects to {output_path}")


if __name__ == "__main__":
    main()
