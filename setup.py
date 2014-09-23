from distutils.core import setup

setup(
        name             = 'seqenv',
        version          = '0.9.0',
        description      = 'Assign environment ontology (EnvO) terms to short DNA sequences',
        long_description = open('README.md').read(),
        license          = 'MIT',
        url              = 'https://bitbucket.org/seqenv',
        author           = 'Umer Zeeshan Ijaz',
        author_email     = 'umer.ijaz@glasgow.ac.uk',
        classifiers      = ['Topic :: Scientific/Engineering :: Bio-Informatics'],
        packages         = ['seqenv'],
        install_requires = ['biopython'],
    )
