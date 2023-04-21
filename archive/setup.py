# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = {"": "src"}

packages = ["defradb"]

package_data = {"": ["*"]}

install_requires = ["requests", "gql[all]"]

setup_kwargs = {
    "name": "defradb",
    "version": "0.0.1",
    "description": "Python client for DefraDB",
    "long_description": None,
    "author": "Orpheus Lummis",
    "author_email": "o@orpheuslummis.info",
    "url": "https://github.com/orpheuslummis/defradb-py",
    "package_dir": package_dir,
    "packages": packages,
    "package_data": package_data,
    "install_requires": install_requires,
    "python_requires": ">=3.10,<3.11",
}

setup(**setup_kwargs)
