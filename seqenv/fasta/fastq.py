# Built-in modules #

# Internal modules #
from seqenv.fasta        import FASTA
from seqenv.common.cache import property_cached

# Third party modules #
import sh

################################################################################
class FASTQ(FASTA):
    """A single FASTQ file somewhere in the filesystem"""

    extension = 'fastq'
    format    = 'fastq'

    @property_cached
    def count(self):
        if self.gzipped: return int(sh.zgrep('-c', "^+$", self.path, _ok_code=[0,1]))
        return int(sh.grep('-c', "^+$", self.path, _ok_code=[0,1]))
