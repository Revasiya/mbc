from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in mbc/__init__.py
from mbc import __version__ as version

setup(
	name="mbc",
	version=version,
	description="MBC",
	author="The ExalterTech",
	author_email="info@exaltertech.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
