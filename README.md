# Seqenv version 0.9
Assign environment ontology (EnvO) terms to short DNA sequences.

### Installing
To install `seqenv` onto your server, use the python package manager:

    $ pip install seqenv

### Usage
Once that is done, you can start processing FASTA files from the command line. For using the default parameters you can just type:

    $ seqenv --in sequences.fasta

We will then assume that you have inputed 16S sequences. To modify the database or use different type of sequence type:

    $ seqenv --in sequences.fasta --seqtype nucl --db nt

To modify the minimum identity in the similarity search, use the following:

    $ seqenv --in sequences.fasta --identity 97

If you have abundance data you would like to add to your analysis you can specify it like this in a TSV file:

    $ seqenv --in sequences.fasta --abundances counts.tsv

### All parameters
   * `--seq_type`: Sequence type `nucl` or `prot` for nucleotides or amino acids, respectively (Default: `nucl`).
   * `--search_algo`: Search algorithm. Either `blast` or `usearch` (Default: `blast`).
   * `--search_db`: The database to search against (Default: `nt`). You can specify the full path or provide a `.ncbirc` file.
   * `--text_source`: Text source: `source` for GenBank record "isolation source" field or `abstractt` for PubMed abstracts (Default: `source`).
   * `--num_threads`: Number of cores to use (Defaults to the total number of cores). Use 1 for non-parallel processing.
   * `--out_dir`: The output directory in which to store the result and intermediary files. Defaults to the same directory as the input file.
   * `--min_identity`: Minimum identity in similarity search (Default: 0.97). Note: not available when using `blastp`.
   * `--e_value`: Minimum e-value in similarity search (Default: 0.0001).
   * `--max_targets`: Maximum number of reference matches in similarity search (Default: 10).
   * `--min_coverage`: Minimum query coverage in similarity search (Default: 0.97).
   * `--abundances`: Abundances file (Default: None).
   * `--N`: If abundances are given, pick only the top N sequences (Default: 1000).
   * `--envo_id`: Extract terms for the given ENVO ID (Default: `all`)
        all=Consider all terms
        Examples:
        ENVO:00010483 = Environmental Material
        ENVO:00002297 = Environmental Features
        ENVO:00000428 = Biome
        ENVO:00002036 = Habitat

### News
* **March 2014**: EnvO tables generated from `SEQenv` can now be visualised in the web browser using `HEAPcloud` [[Source Code](http://userweb.eng.gla.ac.uk/umer.ijaz/bioinformatics/HEAPcloud_v0.1.zip),[Usage](http://userweb.eng.gla.ac.uk/umer.ijaz/bioinformatics/HEAPcloud.pdf)]. The dimensions of the EnvO tables are often large and when we plot the heatmaps using `R`, the data labels sometimes clutter up and the heatmap looks messy. To facilitate a better visualisation and allow interactivity, `HEAPcloud` is a web-based heatmap viewer that in addition to displaying the heatmap can also display a wordcloud highlighting significant terms for each sample (by moving the mouse over the sample names on the right of the heatmap). You can see a demo [here](http://userweb.eng.gla.ac.uk/umer.ijaz/bioinformatics/HEAPcloud_v0.1/HEAPcloud.html) for an example EnvO table.

![HEAPcloud.jpg](https://bitbucket.org/repo/6g996b/images/3218486355-HEAPcloud.jpg)

* **August 2013**: Chris Quince presented a talk on `SEQenv` at [STAMPS2013](https://stamps.mbl.edu/index.php/Main_Page). You can download the PDF of the presentation: [C Quince et. al., SeqEnv: Annotating sequences with environments (STAMPS 2013)](https://stamps.mbl.edu/images/4/44/Quince_SeqEnvSTAMPS2013.pdf)

### Introduction
The continuous drop in the associated costs combined with the increased efficiency of the latest high-throughput sequencing technologies has resulted in an unprecedented growth in sequencing projects. Ongoing endeavours such as the [Earth Microbiome Project](http://www.earthmicrobiome.org) and the [Ocean Sampling Day](http://www.microb3.eu/osd) are transcending national boundaries and are attempting to characterise the global microbial taxonomic and functional diversity for the benefit of mankind. The collection of sequencing information generated by such efforts is vital to shed light on the ecological features and the processes characterising different ecosystems, yet, the full knowledge discovery potential can only be unleashed if the associated meta data is also exploited to extract hidden patterns. For example, with the majority of genomes submitted to NCBI, there is an associated PubMed publication and in some cases there is a GenBank field called "isolation sources" that contains rich environmental information.
With the advances in community-generated standards and the adherence to recommended annotation guidelines such as those of [MIxS](http://gensc.org/gc_wiki/index.php/MIxS) of the Genomics Standards Consortium, it is now feasible to support intelligent queries and automated inference on such text resources.

The [Environmental Ontology](http://environmentontology.org/) will be a critical part of this approach as it gives the ontology for the concise, controlled description of environments. It thus provides structured and controlled vocabulary for the unified meta data annotation, and also serves as a source for naming environmental information. Thus, we have developed the `SEQenv` pipeline capable of annotating sequences with environment descriptive terms occurring within their records and/or in relevant literature. Given a set of sequences, `SEQenv` retrieves highly similar sequences from public repositories (NCBI GenBank). Subsequently, from each of these records, text fields carrying environmental context information (such as the reference title and the **isolation source**) are extracted. Additionally, the associated **PubMed** links are followed and the relevant abstracts are collected. Once the relevant pieces of text for each matching sequence have been gathered, they are then processed by a text mining module capable of identifying EnvO terms mentioned in them. The identified EnvO terms along with their frequencies of occurrence are then subjected to clustering analysis and multivariate statistics. As a result, tagclouds and heatmaps of environment descriptive terms characterizing different sequences/samples are generated. The `SEQenv` pipeline can be applied to any set of nucleotide and protein sequences. Annotation of metagenomic samples, in particular 16S rRNA sequences is also supported.

### Pipeline overview
![SEQenv](https://bitbucket.org/repo/6g996b/images/3493861180-SEQenv.jpg "SEQenv")

### Example XML retrieved from NCBI
![NCBI_eutils.png](https://bitbucket.org/repo/6g996b/images/2991292469-NCBI_eutils.png)

[NCBI’s E-utilities](http://www.ncbi.nlm.nih.gov/books/NBK25499/)** allow the ability to communicate with the databases maintained at NCBI using HTTP POST and QUERY methods. Notable among these are `esearch`, `epost`, `esummary`, and `eLink` services that are used in the pipeline to extract data. The data generated by the web requests can be retrieved in XML format as shown by the two example requests in the figure.  Most popular languages support parsers to manipulate XML files and allow us to extract specific sections (highlighted with red rectangles). Examples of these parsers include `XML::DOM` in `Perl`, `xml.dom.minidom` in `Python`, `org.w3c.dom` and `javax.xml.parsers` in `Java`, and `Xerces` in `C++` to name a few.

### Tutorial
We will first run `seqenv` on a 16S rRNA dataset using ***isolation sources*** as a text source. Here, `All_GoodT_C03.csv` is a species abundance file (3% OTUs) processed through [`AmpliconNoise`](https://code.google.com/p/ampliconnoise/) software and `All_GoodT_C03.fa` contains the corresponding sequences for the OTUs.

~~~
$ ls
All_GoodT_C03.csv
All_GoodT_C03.fa

$ seqenv -o 2 -n 1 -f All_GoodT_C03.fa -s All_GoodT_C03.csv -m 99 -q 99 -r 100
~~~

Once the pipeline has finished processing, you will have the following contents in the current folder:

~~~
$ ls
All_GoodT_C03_N1_blast_F_ENVO_OTUs.csv
All_GoodT_C03_N1_blast_F_ENVO_OTUs_labels.csv
All_GoodT_C03_N1_blast_F_ENVO_samples.csv
All_GoodT_C03_N1_blast_F_ENVO_samples_labels.csv
SEQenv.log
~~~

We are particularly interested in 3 OTUs: C15, C26, and C89 that hold importance in this dataset. We will look inside the `OTUs_dot` folder and open `C15.dot`, `C26.dot`, and `C89.dot` in `GraphViz` (by right-clicking). In the graphs shown below, the observed terms are drawn as boxes and unobserved terms in the lineage are drawn as ellipses. The boxes are then coloured based on their frequency from blue to red with blue corresponding to low frequency terms and red corresponding to high frequency terms, respectively.

![C15.png](https://bitbucket.org/repo/6g996b/images/2965256346-C15.png)

**Figure 4**: C15

![C26.png](https://bitbucket.org/repo/6g996b/images/1171455750-C26.png)

**Figure 5**: C26

![C89.png](https://bitbucket.org/repo/6g996b/images/4162584631-C89.png)

**Figure 6**: C89

Let us now look at the overall profile word cloud (`All_GoodT_C03_N1_blast_F_ENVO_overall_labels.png`) and the heapmap generated in the `samples_heapmap` folder. The heatmap is useful for differentiating/grouping samples based on EnvO frequencies.

![sample_wc.png](https://bitbucket.org/repo/6g996b/images/2053835135-sample_wc.png)

**Figure 7**: Word cloud

![sample_hm.png](https://bitbucket.org/repo/6g996b/images/3830944924-sample_hm.png)

**Figure 8**: Heatmap

The folders `OTUs_dot` and `OTUs_wc` contain digraphs and word clouds for each OTU, respectively. Similarly, the folders `samples_dot` and `samples_wc` contain digraphs and word clouds for each sample, respectively. To further process your data, you can use the frequency tables `All_GoodT_C03_N1_blast_F_ENVO_OTUs_labels.csv` and `All_GoodT_C03_N1_blast_F_ENVO_OTUs_labels.csv` for multivariate statistical analysis. You can also process them in our [`TAXAenv` pipeline](http://quince-srv2.eng.gla.ac.uk:8080/) [[Tutorial](http://userweb.eng.gla.ac.uk/umer.ijaz/TAXAenv_tutorial.pdf)].

If you run the pipeline with `–t 2` switch, i.e. using PubMed abstracts as a text source, you will get the similar contents except that the `documents` will contain the PubMed abstracts with their names corresponding to PubMed IDs.
`SEQenv_sequences.sh` follows the similar workflow as `SEQenv_samples.sh` though it is useful when you don't have any abundance file and you are interested in generating environmental context for any given sequences. For example, given 80 dummy nucleotide sequences (you can also process protein sequences) in FASTA format as `deg_species_filtered.fna`, we will run the pipeline as follows:

~~~
$ ls
deg_species_filtered.fna

$ seqenv -t 1 -p -c 10 -f deg_species_filtered.fna –s nucleotide
~~~

Since the sequences in FASTA format can have long headers, the pipeline first produces a header map file and a FASTA file with modified headers and then processes the new FASTA file instead. You can check the contents of `deg_species_filtered_M.map` to see what individual IDs corresponds to.

~~~
$ head deg_species_filtered_M.map
C1	gi|219846460|ref|NR_026051.1| Caldicellulosiruptor owensensis OL strain OL 16S ribosomal RNA, complete sequence >gi|2454185|gb|U80596.1|COU80596 Caldicellulosiruptor owensense 16S ribosomal RNA gene, partial sequence
C2	gi|265678524|ref|NR_028828.1| Xylanimonas cellulosilytica DSM 15894 strain XIL07 16S ribosomal RNA, complete sequence >gi|22086567|gb|AF403541.1| Xylanomonas cellulosilytica 16S ribosomal RNA gene, partial sequence
C3	gi|343200548|ref|NR_041235.1| Clostridium clariflavum DSM 19732 strain EBR45 16S ribosomal RNA, complete sequence >gi|51036225|dbj|AB186359.1| Clostridium clariflavum gene for 16S rRNA
C4	gi|343200548|ref|NR_041235.1| Clostridium clariflavum DSM 19732 strain EBR45 16S ribosomal RNA, complete sequence >gi|51036225|dbj|AB186359.1| Clostridium clariflavum gene for 16S rRNA
~~~

### Acknowledgments
`SEQenv` was conceived and developed in the following hackathons supported by European Union's Earth System Science and Environmental Management ES1103 COST Action ("[Microbial ecology & the earth system: collaborating for insight and success with the new generation of sequencing tools](http://www.cost.eu/domains_actions/essem/Actions/ES1103)"):

- **From Signals to Environmentally Tagged Sequences** (Ref: ECOST-MEETING-ES1103-050912-018418), September 27th-29th 2012, Hellenic Centre for Marine Research, Crete, Greece
- **From Signals to Environmentally Tagged Sequences II** (Ref: ECOST-MEETING-ES1103-100613-031037), June 10th-13th 2013, Hellenic Centre for Marine Research, Crete, Greece

This work would not have been possible without the advice and support of many people who attended the hackathons:

- [Umer Zeeshan Ijaz](http://userweb.eng.gla.ac.uk/umer.ijaz) (Umer.Ijaz@glasgow.ac.uk) [1,2]
- [Evangelos Pafilis](http://epafilis.info/) (pafilis@hcmr.gr) [1,2]
- [Chris Quince](http://www.gla.ac.uk/schools/engineering/staff/christopherquince/) (cq8u@udcf.gla.ac.uk) [2]
- Christina Pavloudi (cpavloud@hcmr.gr)
- Anastasis Oulas (oulas@hcmr.gr)
- Julia Schnetzer (jschnetz@mpi-bremen.de)
- Aaron Weimann (aaron.weimann@uni-duesseldorf.de)
- Alica Chronakova (alicach@upb.cas.cz)
- Ali Zeeshan Ijaz (alizeeshanijaz@gmail.com)
- Simon Berger (simon.berger@h-its.org)
- Lucas Sinclair (lucas.sinclair@me.com)

[1] Main developers
[2] Contact for correspondence