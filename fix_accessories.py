import os

file_path = 'store/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Restore Men Accessories
content = content.replace(
    "'name': 'Men → Accessories',\n            'image_path': 'images/mens_accessories.png',\n            'route_name': 'under_maintenance_view',",
    "'name': 'Men → Accessories',\n            'image_path': 'images/mens_accessories.png',\n            'route_name': 'accessories_men',"
)

# Restore Women Accessories
content = content.replace(
    "'name': 'Women → Accessories',\n            'image_path': 'images/women-bags.png',\n            'route_name': 'under_maintenance_view',",
    "'name': 'Women → Accessories',\n            'image_path': 'images/women-bags.png',\n            'route_name': 'accessories_women',"
)

# Restore Kids Accessories
content = content.replace(
    "'name': 'Kids → Accessories',\n            'image_path': 'images/kids-accessories.png',\n            'route_name': 'under_maintenance_view',",
    "'name': 'Kids → Accessories',\n            'image_path': 'images/kids-accessories.png',\n            'route_name': 'shared_accessories',"
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Accessories routes restored in store/views.py")
