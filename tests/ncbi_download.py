"""
=======================
Test the NCBI downloads
=======================
"""

# Modules #
from seqenv.eutils import gis_to_records

################################################################################
all_gis = ['6451693', '127', '76365841', '22506766', '389043336', '497',
           '429143984', '264670502', '74268401', '324498487']
all_gis = ['332640072'] # Super long plant chromosome
records = gis_to_records(all_gis)