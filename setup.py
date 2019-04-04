from setuptools import setup

PACKAGE_NAME = 'erlazio_erauzlea'

setup(
    name=PACKAGE_NAME,
    version='1.0',
    description='Bi kontzeptuen arteko erlazio erauzle automatikoa.',
    url='',
    author='Oscar Sainz',
    author_email='osainz59@hotmail.com',
    license='',
    packages=[
        'erlazio_erauzlea',
        'erlazio_erauzlea.corpus',
        'erlazio_erauzlea.corpus.terminoak',
        'erlazio_erauzlea.corpus.distant_supervision',
        'erlazio_erauzlea.sailkatzailea',
        'erlazio_erauzlea.sailkatzailea.ezaugarriak',
        'erlazio_erauzlea.scripts',
        'erlazio_erauzlea.scripts.corpus'
    ],
    install_requires=[
        'numpy',
        'sklearn',
        'scipy',
        'pandas',
        'matplotlib',
        'gensim',
        'mysql-connector-python',
        'imblearn', 'textblob', 'requests', 'spacy'
    ],
    entry_points={
        'console_scripts' : [
            f'{PACKAGE_NAME}.terminoak_erauzi=erlazio_erauzlea.scripts.corpus.terminoak_erauzi:main',
            f'{PACKAGE_NAME}.conceptnet_iragazi=erlazio_erauzlea.scripts.corpus.conceptnet_iragazi:main',
            f'{PACKAGE_NAME}.corpusa_prozesatu=erlazio_erauzlea.scripts.corpus.corpusa_prozesatu:main',
            f'{PACKAGE_NAME}.train_dev_test_zatitu=erlazio_erauzlea.scripts.train_dev_test_zatitu:main',
            f'{PACKAGE_NAME}.train_eval=erlazio_erauzlea.scripts.train_eval:main',
        ]
    }
)