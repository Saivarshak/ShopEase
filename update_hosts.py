import os

path = 'shopease/settings.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

proxy_host = '8000-id6l3eczswqx9keb5drcz-85a1c045.sg1.manus.computer'
if proxy_host not in content:
    content = content.replace(
        "ALLOWED_HOSTS = [",
        f"ALLOWED_HOSTS = [\n    '{proxy_host}',"
    )

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Added {proxy_host} to ALLOWED_HOSTS")
