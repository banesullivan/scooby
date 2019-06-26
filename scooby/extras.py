try:
    import psutil
except ImportError:
    psutil = False

# Get available RAM, if available
if psutil:
    TOTAL_RAM = '{:.1f} GB'.format(psutil.virtual_memory().total / (1024.0 ** 3))
else:
    TOTAL_RAM = False

try:
    import mkl
except ImportError:
    mkl = False
try:
    import numexpr
except ImportError:
    numexpr = False

# Get mkl info from numexpr or mkl, if available
if mkl:
    MKL_INFO = mkl.get_version_string()
elif numexpr:
    MKL_INFO = numexpr.get_vml_version()
else:
    MKL_INFO = False
