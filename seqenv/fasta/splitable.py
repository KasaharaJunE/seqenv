# Futures #
from __future__ import division

# Built-in modules #
import os, sys, math, shutil

# Internal modules #
from seqenv.common.autopaths import DirectoryPath
from seqenv.fasta            import FASTA
from seqenv.fasta.fastq      import FASTQ

# Third party modules #

###############################################################################
class SplitableFASTA(FASTA):
    """A FASTA file which you can split into chunks. Either you give the number
    of parts you want to generate, or you can give a target size in bytes for
    each part."""

    def __init__(self, path, num_parts=None, part_size=None, base_dir=None):
        # Basic #
        self.path = path
        # Directory #
        if base_dir is None: self.base_dir = DirectoryPath(path + '.parts/')
        else:                self.base_dir = DirectoryPath(base_dir)
        # Num parts #
        if num_parts is not None: self.num_parts = num_parts
        # Evaluate size #
        if part_size is not None:
            self.bytes_target = part_size #humanfriendly.parse_size(part_size)
            self.num_parts = int(math.ceil(self.count_bytes / self.bytes_target))
        # Make parts #
        self.make_parts()
        # Give a number to each part #
        for i, part in enumerate(self.parts): part.num = i

    def make_parts(self):
        self.make_name = lambda i: self.base_dir + "%03d/part.fasta" % i
        self.parts = [FASTA(self.make_name(i)) for i in range(1, self.num_parts+1)]

    @property
    def status(self):
        """Has the splitting been done already ?"""
        if all(os.path.exists(p.path) for p in self.parts): return 'splitted'
        return False

    def split(self):
        # Clean up #
        for i in xrange(1, sys.maxint):
            dir_path = self.base_dir + "%03d/" % i
            if os.path.exists(dir_path): shutil.rmtree(dir_path)
            else: break
        # Case only one part #
        if len(self.parts) == 1:
            self.parts[0].directory.create(safe=True)
            self.link_to(self.parts[0])
            return
        # Compute number of sequences #
        self.seqs_per_part = int(math.floor(self.count / self.num_parts))
        # Prepare #
        for part in self.parts: part.create()
        # Do the job #
        seqs = self.parse()
        for part in self.parts:
            for i in xrange(self.seqs_per_part): part.add_seq(seqs.next())
        for seq in seqs: part.add_seq(seq)
        # Clean up #
        for part in self.parts: part.close()

###############################################################################
class SplitableFASTQ(SplitableFASTA, FASTQ):
    """A FASTQ file which you can split into chunks."""

    def make_parts(self):
        self.make_name = lambda i: self.base_dir + "%03d/part.fastq" % i
        self.parts = [FASTQ(self.make_name(i)) for i in range(1, self.num_parts+1)]
