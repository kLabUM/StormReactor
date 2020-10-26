import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="StormReactor",
    version="0.1.0",
    description="StormReactor: Python package for modelling any pollutant generation or removal method in SWMM",
    author="Brooke Mason, Abhiram Mullapudi",
    author_email="bemason@umich.edu, abhiramm@umich.edu",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kLabUM/StormReactor",
    packages=['StormReactor'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "numpy>=1.18.4",
        "pyswmm",
        "scipy",
    ],
    python_requires='>=3.6',
)

