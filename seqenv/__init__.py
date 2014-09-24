b'This module needs Python 2.7.x'

# Special variables #
__version__ = '0.9.0'

# Built-in modules #
import os, multiprocessing
from collections import defaultdict
import cPickle as pickle

# Internal modules #
from seqenv.fasta import FASTA
from seqenv.seqsearch.parallel import ParallelSeqSearch
from seqenv.common.cache import property_cached
from seqenv.eutils import record_to_source, record_to_abstract
from seqenv.common.timer import Timer
from seqenv.common.autopaths import FilePath

# Compiled modules #
import tagger

# Third party modules #
from tqdm import tqdm

# Constants #
home = os.environ['HOME'] + '/'
data_dir = home + "repos/seqenv/data/"

################################################################################
class Analysis(object):
    """The main object. The only mandatory argument is the input fasta file path.
    The text below is somewhat redundant with what is in the readme file and the
    command line utitliy.

    * 'seq_type': Either `nucl` or `prot`. Defaults to `nucl`.

    * `search_algo`: Either 'blast' or 'usearch'. Defaults to `blast`.

    * `search_db`: The path to the database to search against. Defaults to `nt`.

    * `text_source`: Either `source` for isolation source terms or `abstract` for parsing
                     the publication abstracts. Defaults to `source`.

    * `backtracking`: For every term identified by the tagger, we will propagate frequency counts
                      up the acyclic directed graph described by the ontology. Defaults to `False`.

    * `num_threads`: The number of threads. Default to the number of cores on the
                     current machine.

    * `out_dir`: Place all the outputs in the specified directory. Defaults to the input file's directory.

    * Sequence similarity search filtering options:
        - min_identity: Defaults to 0.97
        - e_value: Defaults to 0.0001
        - max_targets: Defaults to 10
        - min_coverage: Defaults to 0.97

    * `abundances`: If you have sample information, then you can provide the
                    'abundances' argument too. It should be a TSV file.

    * `N`: Use only the top `N` sequences in terms of their abundance, discard
           the rest. Only valid if abundances are provided.
    """

    def __init__(self, input_file,
                 seq_type     = 'nucl',
                 search_algo  = 'blast',
                 search_db    = 'nt',
                 text_source  = 'source',
                 backtracking = False,
                 num_threads  = None,
                 out_dir      = None,
                 min_identity = 0.97,
                 e_value      = 0.0001,
                 max_targets  = 10,
                 min_coverage = 0.97,
                 abundances   = None,
                 N            = 1000,):
        # Base parameters #
        self.input_file = FASTA(input_file)
        self.abundances = abundances
        self.N = N
        self.seq_type = seq_type
        self.text_source = text_source
        self.backtracking = backtracking
        # Search parameters #
        self.search_algo = search_algo
        self.search_db = search_db
        # Number of cores to use #
        if num_threads is None: self.num_threads = multiprocessing.cpu_count()
        else: self.num_threads = num_threads
        self.num_threads = min(self.num_threads, self.input_file.count)
        # Hit filtering parameters #
        self.min_identity = min_identity
        self.e_value      = e_value
        self.max_targets  = max_targets
        self.min_coverage = min_coverage
        # Time the pipeline execution #
        self.timer = Timer()
        # Keep all outputs in a directory #
        if out_dir is None: self.out_dir = self.input_file.directory
        else: self.out_dir = self.out_dir
        assert os.path.exists(self.out_dir)

    @property_cached
    def orig_names_to_renamed(self):
        """A dictionary linking every sequence's name in the input FASTA to a
        new name following the scheme "C1", "C2", "C3" etc."""
        return {seq.id:"C%i"%i for i, seq in enumerate(self.input_file)}

    @property
    def renamed_fasta(self):
        """Make a new fasta file where every name in the input FASTA file is replaced
        with "C1", "C2", "C3" etc. Returns this new FASTA file."""
        renamed_fasta = FASTA(self.input_file.prefix_path + '_renamed.fasta')
        if renamed_fasta.exists: return renamed_fasta
        print "STEP 1: Generate mappings for sequence headers in FASTA file."
        self.input_file.rename_sequences(renamed_fasta, self.orig_names_to_renamed)
        self.timer.print_elapsed()
        return renamed_fasta

    @property
    def only_top_sequences(self):
        """Make a new fasta file where only the top N sequences are included
        (in terms of their abundance)."""
        if not self.abundances: return self.renamed_fasta
        only_top_fasta = FASTA(self.input_file.prefix_path + '_top.fasta')
        if only_top_fasta.exists: return only_top_fasta
        print "Using: " + self.renamed_fasta
        print "STEP 1B: Get the top %i sequences (in terms of their abundances)." % self.N
        self.timer.print_elapsed()
        #TODO
        return only_top_fasta

    @property_cached
    def filtering(self):
        """Return a dictionary with the filtering options for the sequence similarity
        search."""
        return {
            'min_identity': self.min_identity,
            'e_value':      self.e_value,
            'max_targets':  self.max_targets,
            'min_coverage': self.min_coverage,
        }

    @property_cached
    def search(self):
        """The similarity search object with all the relevant parameters."""
        return ParallelSeqSearch(input_fasta = self.only_top_sequences,
                                 seq_type    = self.seq_type,
                                 algorithm   = self.search_algo,
                                 database    = self.search_db,
                                 num_threads = self.num_threads,
                                 filtering   = self.filtering)

    @property
    def search_results(self):
        """For every sequence, search against a database and return the best hits
        after filtering."""
        # Check that the search was run #
        if not self.search.out_path.exists:
            print "Using: " + self.only_top_sequences
            print "STEP 2: Similarity search against the '%s' database" % self.search_db
            self.search.run()
            self.timer.print_elapsed()
            print "STEP 3: Filter out bad hits from the search results"
            self.search.filter()
            self.timer.print_elapsed()
        # Parse the results #
        return self.search.results

    @property_cached
    def seq_to_gis(self):
        """A dictionary linking every input sequence to a list of gi identifiers found
        that are relating to it."""
        result = defaultdict(list)
        for hit in self.search_results:
            seq_name = hit[0]
            gi = hit[1].split('|')[1]
            result[seq_name].append(gi)
        return result

    @property_cached
    def gi_to_text(self):
        """A dictionary linking every gi identifier to some unspecified text blob.
        Typically the text is its isolation source or a list of abstracts."""
        # Check that it was run #
        text_entries = FilePath(self.out_dir + 'gi_to_text.pickle')
        if not text_entries.exists:
            result = {}
            unique_gis = set(gi for gis in self.seq_to_gis.values() for gi in gis)
            print "STEP 4: Download data from NCBI"
            all_records = gis_to_records(unique_gis)
            if self.text_source == 'source': fn = record_to_source
            if self.text_source == 'abstract': fn = record_to_abstract
            for gi, record in all_records.items():
                text = fn(gi)
                if text is not None: result[gi] = text
            with open(text_entries, 'w') as handle: pickle.dump(result, handle)
            self.timer.print_elapsed()
            return result
        # Parse the results #
        with open(text_entries, 'r') as handle: return pickle.load(handle)

    @property_cached
    def gi_to_concepts(self):
        """A dictionary linking every `gi` identifier to the concept counts.
        (dictionaries of concept:int). This is done by finding regions of interest in the text
        (i.e. a match). We can assign meaning to the matches in terms of concepts.
        A 'concept' or 'entity' here would be an envo term such as 'ENVO:01000047'
        When you call `t.GetMatches(python_string, "", [-27])` you get a list back.
        The second argument can be left empty in our case (per document blacklisting)
        The result is something like:
        - [(53, 62, ((-27, 'ENVO:00002001'),)), (64, 69, ((-27, 'ENVO:00002044'),))]
        The number -27 is ENVO terms, -26 could be tissues, etc.
        """
        # Call the tagger
        print "STEP 5: Run the text mining tagger on NCBI results."
        t = tagger.Tagger()
        # Load the dictionary #
        t.LoadNames('data/envo_entities.tsv', 'data/envo_names.tsv')
        # Load a global blacklist #
        t.LoadGlobal('data/envo_global.tsv')
        # Tag all the text #
        result = defaultdict(lambda: defaultdict(int))
        for gi, text in self.gi_to_text.items():
            matches = t.GetMatches(text, "", [-27])
            for start_pos, end_pos, concepts in matches:
                ids = set([concept_id for concept_type, concept_id in concepts])
                if self.backtracking: ids.update([p for c in ids for p in self.child_to_parents[c]])
                for concept_id in ids: result[gi][concept_id] +=1
        # Return #
        self.timer.print_elapsed()
        return result
        # TODO If backtracking is activated, add all the parent terms for every child term

    @property_cached
    def serial_to_concept(self):
        """Lorem ipsum. This could overflow the memory."""
        result = {}
        with open(data_dir + 'envo_entities.tsv') as handle:
            for line in handle:
                serial, concept_type, concept_id = line.split()
                result[serial] = concept_id
        return result

    @property_cached
    def child_to_parents(self):
        """Lorem ipsum. This could overflow the memory."""
        result = defaultdict(list)
        with open(data_dir + 'envo_groups.tsv') as handle:
            for line in handle:
                child_serial, parent_serial = line.split()
                child_concept = self.serial_to_concept[child_serial]
                parent_concept = self.serial_to_concept[parent_serial]
                result[child_concept].append(parent_concept)
        return result

    def generate_freq_tables(self):
        """Generate the frequencies tables..."""
        if not somefile.exists:
            print "Using %i results from the text mining results" % len(tagger_results)
            print "STEP 6: Generating main output."
        else:
            print "Final results already exist !"

    def generate_dot_files(self):
        """Generate the dot files for visualization in GraphViz..."""
        pass