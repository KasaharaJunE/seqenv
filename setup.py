from distutils.core import setup

setup(
      name             = 'seqenv',
      version          = '1.0.6',
      description      = 'Assign environment ontology (EnvO) terms to short DNA sequences',
      long_description = open('README.md').read(),
      license          = 'MIT',
      url              = 'https://github.com/xapple/seqenv',
      download_url     = 'https://github.com/xapple/seqenv/tarball/1.0.6',
      author           = 'Lucas Sinclair',
      author_email     = 'lucas.sinclair@me.com',
      classifiers      = ['Topic :: Scientific/Engineering :: Bio-Informatics'],
      packages         = ['seqenv'],
      scripts          = ['seqenv/seqenv'],
      install_requires = ['biopython', 'sh', 'pandas', 'tqdm', 'biom-format', 'requests'],
    )
