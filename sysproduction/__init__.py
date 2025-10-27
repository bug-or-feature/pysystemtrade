import sys
import os

prod_path = f"{os.getenv('PYSYS_CODE')}/sysproduction"
if prod_path in sys.path:
    sys.path.remove(prod_path)
