from setuptools import find_packages
from setuptools import setup

#with open("README.md", "r") as fh:
#    long_description = fh.read()
description = "A simple flask based microblogging cms written in python."

setup(
    name="blog-pkg-rangirangi",
    version="0.0.1",
    license="BSD",
    url="https://github.com/alefmim/RangiRangi/",
    author="AlefMim",
    author_email="mralefmim@gmail.com",
    description=description,
    long_description=description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)