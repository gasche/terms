import distribute_setup
distribute_setup.use_setuptools()
from setuptools import setup

VERSION = '0.1.0a1'

setup(
    name = 'Terms',
    version = VERSION,
    author = 'Enrique Pérez Arnaud',
    author_email = 'enriquepablo@gmail.com',
    url = 'http://pypi.python.org/terms.core',
    license = 'GNU GENERAL PUBLIC LICENSE Version 3',
    description = 'A smart knowledge store',
    long_description = open('INSTALL.txt').read() + open('README.txt').read(),

    packages = ['terms', 'terms.core',],
    namespace_packages = ['terms'],
    py_modules = ['distribute_setup'],
    test_suite = 'nose.collector',
    include_package_data = True,

    entry_points = {
        'console_scripts': [
            'terms = terms.core.repl:repl',
            'initterms = terms.core.scripts.initterms:init_terms',
        ],
    },
    tests_require = [
        'Nose',
        'coverage',
    ],
    install_requires = [
        'psycopg2 == 2.4.5',
        'sqlalchemy == 0.7.8',
        'ply == 3.4',
    ],
)
