from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

__version__ = "0.5.8"

# Get the long description from the README file
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
    name="vfbquery",
    version=__version__,
    description="Wrapper for querying VirtualFlyBrain knowledge graph.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VirtualFlyBrain/VFBquery",
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
    install_requires=[
        "pysolr",
        "pandas",
        "marshmallow",
        "vfb_connect"
    ],
    python_requires=">=3.7",
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/VirtualFlyBrain/VFBquery/issues',
        'Source': 'https://github.com/VirtualFlyBrain/VFBquery'
    },
)
