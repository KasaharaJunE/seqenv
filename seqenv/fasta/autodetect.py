# Built-in modules #

# Internal modules #
from seqenv.fasta       import FASTA
from seqenv.fasta.fastq import FASTQ

# Third party modules #

###############################################################################
def fasta_or_fastq(path):
    if ".fastq" in path: return FASTQ(path)
    return FASTA(path)