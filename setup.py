import glob
import setuptools

setuptools.setup(
    name='start_dbi',
    version='0.0.1',
    description='Provides the DBI module for START.',
    author='Deby Katz; Chris Timperley',
    author_email='dskatz@gmail.com; christimperley@gmail.com',
    url='https://github.com/squaresLab/start-dbi',
    install_requires=[
        'start-core',
        'numpy',
        'sklearn'
    ],
    packages=['start_dbi']
)
