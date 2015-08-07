#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
A script to parse and download information from the NCBI NT database
useful for the seqenv project.

Written by Lucas Sinclair.
Kopimi.

You can use this script from the shell like this::
$ ./generate.py
"""

# Built-in modules #
import os, time, sqlite3

# Internal modules #
from seqenv.common.timer import Timer
from seqenv.common.autopaths import FilePath

# Third party modules #
from Bio import Entrez
from Bio.Entrez.Parser import CorruptedXMLError
from tqdm import tqdm
from shell_command import shell_output

# Constants #
Entrez.email = "I don't know who will be running this script"
at_a_time = range(2)

# Get current directory #
current_dir = os.getcwd() + '/'
current_dir = os.path.dirname(os.path.realpath(__file__)) + '/'

# Files #
gids_file = FilePath(current_dir + 'all_gis.txt')
sqlite_file = FilePath(current_dir + 'gi_to_source.tsv')

# Check #
msg = 'The database "%s" already exists.' % sqlite_file
msg += ' Delete it before running this script to recreate it.'
if sqlite_file.count_bytes > 0: raise Exception(msg)

###############################################################################
def all_gis(timer=None):
    if gids_file.count_bytes < 1:
        print 'STEP 1: Get all GIs from local nt database into a file (about 6h).'
        shell_output("blastdbcmd -db nt -entry all -outfmt '%g' > " + gids_file)
        if timer is not None: timer.print_elapsed()
    else:
        print 'All gi numbers already found in file "%s", skipping STEP 1.' % gids_file
    return gids_file

###############################################################################
def gis_to_records(gids_file):
    """Download information from NCBI in batch mode"""
    print 'STEP 2: Querying NCBI and writing to database'
    for i in tqdm(range(0, len(gids_file), len(at_a_time))):
        chunk      = [gids_file.next() for _ in at_a_time]
        records    = chunk_to_records(chunk)
        sources    = map(record_to_source, records)
        pubmed_ids = map(record_to_pubmed_id, records)
        yield (dict(zip(chunk, zip(sources, pubmed_ids))))

def chunk_to_records(chunk):
    """Download from NCBI until it works. Will restart until reaching the python
    recursion limit. We don't want to get our IP banned from NCBI so we have
    a little pause at every function call."""
    time.sleep(0.5)
    try:
        response = Entrez.efetch(db="nucleotide", id=chunk, retmode="xml")
        records = list(Entrez.parse(response, validate=True))
        return records
    except CorruptedXMLError:
        return chunk_to_records(chunk)

def record_to_source(record):
    qualifiers = record['GBSeq_feature-table'][0]['GBFeature_quals']
    for qualifier in qualifiers:
        if qualifier['GBQualifier_name'] == 'isolation_source':
            return qualifier['GBQualifier_value']

def record_to_pubmed_id(record):
    references = record['GBSeq_references'][0]
    pubmed_id = references.get('GBReference_pubmed')
    return pubmed_id

###############################################################################
def add_to_database(results):
    if os.path.exists(sqlite_file): os.remove(sqlite_file)
    with sqlite3.connect(sqlite_file) as connection:
        cursor = connection.cursor()
        cursor.execute("CREATE table 'data' (gi integer, source text, pubid integer)")
        sql_command = "INSERT into 'data' values (?,?,?)"
        for chunk in results:
            values = ((gi, info[0], info[1]) for gi, info in chunk.iteritems())
            cursor.executemany(sql_command, values)
        cursor.execute("CREATE INDEX if not exists 'data_index' on 'data' (gi)")
        connection.commit()
        cursor.close()

###############################################################################
def test():
    """Test this script"""
    # Just a bunch of random GI numbers #
    test_gis = ['6451693', '127', '76365841', '22506766', '389043336',
                '497', '429143984', '264670502', '74268401', '324498487']
    # The result we should get #
    template_result = """
    74268401,None,None
    6451693,None,None
    76365841,Everglades wetlands,16907754
    324498487,bacterioplankton sample from lake,None
    389043336,lake water at 5 m depth during dry season,None
    22506766,None,None
    127,None,None
    429143984,downstream along river bank,None
    497,None,3120795
    264670502,aphotic layer; anoxic zone; tucurui hydroeletric power plant reservoir,None
    """
    # Make it pretty #
    template_result = '\n'.join(l.lstrip(' ') for l in template_result.split('\n') if l)
    # The result we got #
    results = gis_to_records(test_gis)
    # Function #
    def result_dict_to_lines(results):
        for gi, info in results.iteritems():
            yield gi + ',' + str(info[0]) + ',' + str(info[1]) + '\n'
    # Check #
    text_version = ''.join(result_dict_to_lines(results))
    assert text_version == template_result
    # Return #
    return results

###############################################################################
if __name__ == '__main__':
    # Start timer #
    timer = Timer()
    timer.print_start()

    # Test the pipeline #
    print 'STEP 0: Testing the script and connection'
    test()

    # Do it #
    add_to_database(gis_to_records(all_gis(timer)))

    # End #
    print 'Done. Results are in "%s"' % os.path.abspath(current_dir)
    timer.print_end()
    timer.print_total_elapsed()