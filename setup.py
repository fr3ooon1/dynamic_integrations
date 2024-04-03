from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in dynamic_integrations/__init__.py
from dynamic_integrations import __version__ as version

setup(
	name="dynamic_integrations",
	version=version,
	description="Dynamic Integrations",
	author="Dynamic Technology",
	author_email="info@dynamiceg.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
