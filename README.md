# StormReactor: Python package for modeling any pollutant generation or treatment method in EPA SWMM
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

## Overview 

*StormReactor* was developed to expand the ability to model stormwater quality and water quality based real-time control in EPA's Stormwater Management Model (SWMM). It is a natural extension of *Open-Storm*'s(http://open-storm.org/) mission to open up and ease access into the technical world of smart stormwater systems. *StormReactor* enables users to model any stormwater pollutant treatment or generation method in any node or link in a stormwater network. A user can implement any SWMM treatment function defined in the *SWMM Reference Manual Volume III: Water Quality* or create their own.   


## Getting Started 

### Installation 

**Requirements**

- python 3.6+
- numpy
- pyswmm
- scipy

We are waiting on the SWMM pull request to be accepted. You can find our pull request here: https://github.com/OpenWaterAnalytics/Stormwater-Management-Model/pull/302. The issue has also been raised on the PySWMM repository here: https://github.com/OpenWaterAnalytics/pyswmm/issues/230. Once the pull request has been approved for SWMM, a similar PySWMM pull request will be initiated. Then, the final version of StormReactor will be available 
through PyPI at https://pypi.python.org/pypi/StormReactor/.

```bash 
$ pip install StormReactor
```

For now, please download directly from the following GitHub repositories.  
StormReactor: https://github.com/kLabUM/StormReactor  
Modified PySWMM: https://github.com/bemason/pyswmm_BM  
Modified SWMM: https://github.com/bemason/SWMM_BM  

Please raise an issue on the repository or reach out if you run into any issues installing or using the package. 

### Example 1

Here is a simple example on how to use *StormReactor* for modeling a variety of water quality methods (e.g., gravity settling, erosion) for a pollutant (e.g., TSS) in several stormwater assets (e.g., basin, channel). This example covers all existing pollutant treatment and generation methods in *StormReactor* except a completely stirred tank reactor (CSTR). Please see the next example for modeling a CSTR.

```python 
# import packages
import StormReactor
from pyswmm import Simulation

# build water quality configuration dictionary
config = {'detention_basin': { 'pollutant': 0, 'method': 'GravitySettling', 'parameters': {'k': 0.0005, 'C_s': 21.0}},\
			'channel': { 'pollutant': 0, 'method': 'Erosion', 'parameters': {'w': 10.0, 'So': 0.037, 'Ss': 1.6, 'd50': 0.04}},\
					{ 'pollutant': 0, 'method': 'GravitySettling', 'parameters': {'k': 0.0005, 'C_s': 21.0}}}


# initialize water quality
with Simulation('example1.inp') as sim:
	WQ = waterQuality(sim, config)

	for step in sim:
		# update each time step
		WQ.updateWQState()

```

### Example 2

Here is a simple example for modeling a CSTR for a pollutant (e.g., nitrate) in several stormwater assets (e.g., basin, wetland). Note you must call <updateWQState_CSTR(index)> instead of <updateWQState()> because the CSTR code requires the additonal input of <index>. This is the only difference for modeling a CSTR.

```python 
# import packages
import StormReactor
from pyswmm import Simulation

# build water quality configuration dictionary
config = {'detention_basin': { 'pollutant': 0, 'method': 'CSTR', 'parameters': {'k': -0.0005, 'n': 1.0, 'Co': 10.0}},\
			'wetland': { 'pollutant': 0, 'method': 'CSTR', 'parameters': {'k': -0.000089, 'n': 3.0, 'Co': 10.0}}}


# initialize water quality
with Simulation('example2.inp') as sim:
	WQ = waterQuality(sim, config)

	for step in sim:
		# update each time step
		WQ.updateWQState_CSTR(index)

```

## Creating Your Own Water Quality Method

To create a new water quality method, follow the steps below:
1. Fork the repository to your own personal repository.
2. Add the name of your new method to the water quality methods definition in waterQuality() within waterQuality.py
```python 
# Water quality methods
self.method = {
    "EventMeanConc": self._EventMeanConc,
    "ConstantRemoval": self._ConstantRemoval,
    "CoRemoval": self._CoRemoval,
    "ConcDependRemoval": self._ConcDependRemoval,
    "NthOrderReaction": self._NthOrderReaction,
    "kCModel": self._kCModel,
    "GravitySettling": self._GravitySettling,
    "Erosion": self._Erosion,
    "CSTR": self._CSTRSolver,
    "NewMethod": self._NewMethod
    }
```
3. Add the definition of your new water quality method to the end of waterQuality() within waterQuality.py. Be sure to include all the necessary method inputs including self, ID, pollutant_ID, dictionary, and flag. You can use any of the PySWMM/SWMMM getters to get necessary water quantity and quality values for your model. Also be sure to set "parameters = dictionary" so that you can access your inputs in your dictionary. Once your model code is added, don't forget to set the new node and link concentrations in SWMM using the appropriate setters.
```python 
def _NewMethod(self, ID, pollutant_ID, dictionary, flag):
	"""
	Add method description and required parameters.
	"""
	# Set parameters = dictionary so you can access your dictionary parameters.
	parameters = dictionary

	"""
	CODE BLOCK
	New method code to calculate new pollutant concentration, here referred to as Cnew.
	Set the concentration in SWMM using the appropriate setters using the flag feature.
	"""
	if self.flag == 0:
		self.sim._model.setNodePollutant(ID, pollutant_ID, Cnew)
	else:
		self.sim._model.setLinkPollutant(ID, pollutant_ID, Cnew)
	
```
4. Now run your new model! Modify code as needed.

## Bugs

Our issue tracker is at https://github.com/kLabUM/StormReactor/issues. Please report any bugs that you find. Or even better, fork the repository on GitHub and create a pull request. All changes are welcome, big or small, and we will help make the pull request if you are new to git (just ask on the issue).

## Contributions

If you want to contribute your water quality methods to *StormReactor*, please follow these steps:
1. Raise an issue on the issue tracker at https://github.com/kLabUM/StormReactor/issues to describe the new method you are proposing to add. 
2. Follow the steps above in "Creating Your Own Water Quality Method" to build your new method. 
3. Create tests to confirm your new method works. Please follow the format for node and link tests as shown at https://github.com/kLabUM/StormReactor/tree/master/tests. 
4. Submit a pull request at https://github.com/kLabUM/StormReactor/pulls to merge your edits with the existing *StormReactor* code base.
Note: There might be comments, suggestions, and questions. We're all working together to produce cohesive and high-quality software.
