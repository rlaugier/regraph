import sys

from setuptools import setup

setup(name='regraph',
      version='0.1', # defined in the __init__ module
      description='A python tool to visualize requirement lists for instrument design',
      url='--',
      author='Romain Laugier',
      author_email='romain.laugier@kuleuven.be',
      license='',
      classifiers=[
          'Development Status :: 3 - pre-Alpha',
          'Intended Audience :: Professional astronomers system engineers',
          'Topic :: High Angular Resolution Astronomy :: Interferometry',
          'Programming Language :: Python :: 3.7'
      ],
      packages=['regraph'],
      install_requires=[
        "streamlit","graphviz", "astropy", "textwrap"
    ],
      include_package_data=True,
      zip_safe=False)
