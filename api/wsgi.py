import sys
print(sys.path, file=sys.stderr)
from api.app import init_pf_db
init_pf_db()
from api.app import app as application