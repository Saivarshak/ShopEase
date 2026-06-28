content = open('store/views.py').read()
old_str = \
status_message
:
Our accessories section is currently under maintenance.
\
content = content.replace(old_str, \
status_message
:

\)
open('store/views.py', 'w').write(content)
