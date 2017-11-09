import os
from setuptools import setup
import sys

distmeta = {}
for line in open(os.path.join('gene_viz', '__init__.py')):
    try:
        field, value = (x.strip() for x in line.split('='))
    except ValueError:
        continue
    if field == '__version_info__':
        value = value.strip('[]()')
        value = '.'.join(x.strip(' \'"') for x in value.split(','))
    else:
        value = value.strip('\'"')
    distmeta[field] = value
    
long_description = "See {}".format(distmeta["__homepage__"])

setup(
    name="gene_viz",
    version=distmeta["__version_info__"],
    description="A python library for the vizualization of gene structure",
    long_description=long_description,
    author=distmeta["__author__"],
    author_email=distmeta["__contact__"],
    url=distmeta["__homepage__"],
    license="MIT",
    platforms=["linux"],
    packages=["gene_viz"],
    python_requires='>=2.7',
    install_requires=[
        "bokeh",
        "pandas",
    ],
    entry_points={
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
    ],
    keywords = "bioinformatics visualization genetics"
)
