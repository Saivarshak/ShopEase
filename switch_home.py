import os

path = 'templates/store/home.html'
restored_path = 'templates/store/home_restored.html'

if os.path.exists(restored_path):
    # Backup current home.html
    if not os.path.exists('templates/store/home_backup.html'):
        os.rename(path, 'templates/store/home_backup.html')
    else:
        os.remove(path)
    
    # Replace with restored version
    os.rename(restored_path, path)
    print("Home page template switched to restored version.")
else:
    print("Restored template not found.")
