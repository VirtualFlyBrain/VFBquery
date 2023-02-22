from setuptools import setup, find_packages
from os import path
from get_version import get_version

here = path.abspath(path.dirname(__file__))

__version__ = get_version(__file__)
del get_version

# TODO for test deployment
# __version__ = "0.0.1.dev1"

# Get the long description from the README file
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
    name="vfb_queries",
    version=__version__,
    description="Wrapper for querying VirtualFlyBrain knowledge graph.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VirtualFlyBrain/VFB_queries",
    author="VirtualFlyBrain",
    license="GPL-3.0 License",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    include_package_data=True,
    install_requires=["vfb_connect", "dataclasses-json", "dacite", "requests", "pysolr"],
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/VirtualFlyBrain/VFB_queries/issues',
        'Source': 'https://github.com/VirtualFlyBrain/VFB_queries'
    },
)