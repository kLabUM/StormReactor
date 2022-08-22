import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="StormReactor",
    version="1.0.0",
    description="StormReactor: Python package for modelling any pollutant generation or treatment method in SWMM",
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
        "numpy>=1.21.2",
        "pyswmm>=1.2.0",
        "scipy>=1.7.1",
    ],
    python_requires='>=3.6',
)

