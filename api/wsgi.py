import sys
print(sys.path, file=sys.stderr)

from api.app import app as application