import os
import re

file_path = 'store/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Restore Women Accessories
content = re.sub(
    r"'name':\s*'Women\s*→\s*Accessories',\s*'image_path':\s*'images/womens_accessories\.png',\s*'route_name':\s*'under_maintenance_view'",
    "'name': 'Women → Accessories', 'image_path': 'images/womens_accessories.png', 'route_name': 'accessories_women'",
    content
)

# Restore Kids Accessories
content = re.sub(
    r"'name':\s*'Kids\s*→\s*Accessories',\s*'image_path':\s*'images/kids_accessories\.png',\s*'route_name':\s*'under_maintenance_view'",
    "'name': 'Kids → Accessories', 'image_path': 'images/kids_accessories.png', 'route_name': 'shared_accessories'",
    content
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Accessories routes restored in store/views.py using corrected regex")
