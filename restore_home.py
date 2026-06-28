content = open('store/views.py').read()
content = content.replace(\
route_name
:
under_maintenance_view
\, \route_name:
accessories_men
\, 1)
content = content.replace(\
route_name
:
under_maintenance_view
\, \route_name:
accessories_women
\, 1)
content = content.replace(\
route_name
:
under_maintenance_view
\, \route_name:
shared_accessories
\, 1)
open('store/views.py', 'w').write(content)
