import pytest
from StormReactor import waterQuality, PySWMMStepAdvanceNotSupported
from pyswmm import Simulation, Nodes

from StormReactor.tests.inps import (model_constantinflow_constanteffluent)

def test_step_advnace_exception_updateWQState():
    with pytest.raises(PySWMMStepAdvanceNotSupported):
        dict1 = {'Tank': {'type': 'node',
                          'pollutant': 'P1',
                          'method': 'EventMeanConc',
                          'parameters': {'C': 5.0}}}
        with Simulation(model_constantinflow_constanteffluent) as sim:
            EMC = waterQuality(sim, dict1)
            sim.step_advance(300)
            for step in sim:
                EMC.updateWQState()


def test_step_advnace_exception_updateWQState_CSTR():
    with pytest.raises(PySWMMStepAdvanceNotSupported):
        dict1 = {'Tank': {'type': 'node',
                          'pollutant': 'P1',
                          'method': 'CSTR',
                          'parameters': {'k': -0.2, 'n': 1.0, 'c0': 10.0}}}

        with Simulation(model_constantinflow_constanteffluent) as sim:
            CS = waterQuality(sim, dict1)
            sim.step_advance(300)
            for index,step in enumerate(sim):
                CS.updateWQState_CSTR(index)
