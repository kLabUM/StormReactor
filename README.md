# StormReactor: Python package for modeling any pollutant generation or removal method in SWMM
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

## Overview 

This library has been developed in an effort to systematize quantitative analysis of stormwater control algorithms. It is a natural extension of the Open-Storm's mission to open up and ease access into the technical world of smart stormwater systems. We have now developed a toolbox so that anyone can model any stormwater pollutant treatment method in any node or link. One can implement any SWMM treatment or any user-defined treatment.   


## Getting Started 

### Installation 

**Requirements**

- python 3+
- numpy
- pyswmm
- scipy


```bash 
pip install StormReactor
```

Please raise an issue on the repository or reach out if you run into any issues installing the package. 

### Example 

Here is an example implementation on how you would use this library for evaluating the ability of a rule based control in maintaining the flows in a network below a desired threshold. 

```python 
import StormReactor
from pyswmm import Simulations,Nodes

# Enter example here

```
