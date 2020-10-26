# StormReactor: Python package for modeling any pollutant generation or removal method in SWMM
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

## Overview 

This package has been developed in an effort to expand the ability to model stormwater quality and water quality based real-time control. It is a natural extension of Open-Storm's mission to open up and ease access into the technical world of smart stormwater systems. This package enables anyone to model any stormwater pollutant treatment or generation method in any node or link in a stormwater network. A user can implement any SWMM treatment function defined in the SWMM Reference Manual Volume III: Water Quality or create their own.   


## Getting Started 

### Installation 

**Requirements**

- python 3.6+
- numpy
- pyswmm
- scipy


```bash 
pip install StormReactor
```

Please raise an issue on the repository or reach out if you run into any issues installing the package. 

### Example 

Here is an example implementation on how you would use this package for evaluating the ability of a rule based control in maintaining the flows in a network below a desired threshold. 

```python 
# import packages
import StormReactor
from pyswmm import Simulation

# build water quality configuration dictionary
config = {'detention_basin': { 'pollutant': 0, 'method': 'GravitySettling', 'parameters': {'k': 0.01, 'C_s': 10.0}},\
			'wetland': { 'pollutant': 1, 'method': 'CSTR', 'parameters': {'k': -0.20, 'n': 1.0, 'Co': 0.0}},\
			'channel': { 'pollutant': 0, 'method': 'Erosion', 'parameters': {'w': 10.0, 'So': 0.001, 'Ss': 2.68, 'd50': 0.7}},\
					{ 'pollutant': 0, 'method': 'GravitySettling', 'parameters': {'k': 0.01, 'C_s': 10.0}}}


# initialize water quality
with Simulation('example.inp') as sim:
	WQ = waterQuality(sim, config)

	for step in sim:
		# update each time step
		WQ.updateWQState()

```
