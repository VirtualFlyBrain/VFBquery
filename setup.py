from setuptools import setup, find_packages
from os import path
import glob

here = path.abspath(path.dirname(__file__))

from get_version import get_version
__version__ = get_version(__file__)
del get_version

# Get the long description from the README file
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(name='vfbquery',  # Required
      version=__version__,  # Required
      packages=find_packages(where='src'),
      package_dir={'': 'src'},
      py_modules=[path.splitext(path.basename(path))[0] for path in glob.glob('src/*.py')],
      include_package_data=True,
      description='Wrapper for querying VirtualFlyBrain servers.',  # Optional)
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Robert Court',  # Optional
      url='https://github.com/VirtualFlyBrain/VFBquery',
      # This should be a valid email address corresponding to the author listed
      # above.
      author_email='rcourt@ed.ac.uk',  # Optional
      install_requires=['requests', 'pandas', 'jsonpath_rw'],
      classifiers=[  # Optional
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 3',
       ],
      project_urls={  # Optional
          'Bug Reports': 'https://github.com/VirtualFlyBrain/VFBquery/issues',
          'Source': 'https://github.com/VirtualFlyBrain/VFBquery',
          'Documentation': 'https://virtualflybrain.org'
       },
)
