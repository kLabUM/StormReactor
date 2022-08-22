from StormReactor import waterQuality
from pyswmm import Simulation, Nodes, Links
import numpy as np
from sklearn.metrics import mean_squared_error as mse
import pytest

"""
SWMM Water Quality Methods:
For each method, check the root mean square error between the toolbox 
computed concentration and the SWMM computed concentration for the 
entire simulation is below 0.06.

For each method, check the percent change between the final outfall load
computed by the toolbox and by SWMM is less than 0.03.

Additional Water Quality Methods:
For each method, check the cummulative load in the node where the 
pollutant transformation is occurring is equivalent to the cummulative 
load downstream.

Additionally, for CSTR, check the toolbox's calculated steady state 
concentration is equal to the closed form steady state CSTR equation. 
"""


# SWMM WATER QUALITY METHODS
# Event Mean Concentration
def test_EventMeanConc_conc():
    dict1 = {'Tank': {'pollutant': 'P1', 'method': 'EventMeanConc', 'parameters': {'C': 5.0}}}
    conc = []
    con = []
    with Simulation("./inps/model_constantinflow_constanteffluent.inp") as sim:
        EMC = waterQuality(sim, dict1)
        Tank1 = Nodes(sim)["Tank"]
        for step in sim:
            EMC.updateWQState()
            c = Tank1.pollut_quality
            conc.append(c['P1'])
    with Simulation("./inps/model_constantinflow_constanteffluent_emc.inp") as sim:
        Tank1 = Nodes(sim)["Tank"]
        for step in sim:
            co = Tank1.pollut_quality
            con.append(co['P1'])
    error = mse(con, conc, squared=True)
    print(error)
    assert error <= 0.06

def test_EventMeanConc_load():
    dict1 = {'Tank': {'pollutant': 'P1', 'method': 'EventMeanConc', 'parameters': {'C': 5.0}}}
    conc = []
    conc1 = []
    flow = []
    flow1 = []
    with Simulation("./inps/model_constantinflow_constanteffluent.inp") as sim:
        EMC = waterQuality(sim, dict1)
        Outfall = Nodes(sim)["Outfall"]
        for step in sim:
            EMC.updateWQState()
            c = Outfall.pollut_quality
            conc.append(c['P1'])
            flow.append(sim._model.getNodeResult("Outfall",0))
        load = [a*b for a,b in zip(conc,flow)]
        cum_load = np.cumsum(load)
    with Simulation("./inps/model_constantinflow_constanteffluent_emc.inp") as sim:
        Outfall = Nodes(sim)["Outfall"]
        for step in sim:
            c = Outfall.pollut_quality
            conc1.append(c['P1'])
            flow1.append(sim._model.getNodeResult("Outfall",0))
        load1 = [a*b for a,b in zip(conc1,flow1)]
        cum_load1 = np.cumsum(load1)    
    error = (cum_load1[-1]/cum_load[-1])/cum_load1[-1]
    print(error)
    assert error <= 0.03


# Constant Removal
def test_ConstantRemoval_conc():
    dict1 = {'Tank': {'pollutant': 'P1', 'method': 'ConstantRemoval', 'parameters': {'R': 0.5}}}
    conc = []
    con = []
    with Simulation("./inps/model_constantinflow_constanteffluent.inp") as sim:
        CR = waterQuality(sim, dict1)
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            CR.updateWQState()
            c = Tank.pollut_quality
            conc.append(c['P1'])
    with Simulation("./inps/model_constantinflow_constanteffluent_constantremoval.inp") as sim:
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            co = Tank.pollut_quality
            con.append(co['P1'])
    error = mse(con, conc, squared=True)
    print(error)
    assert error <= 0.06

def test_ConstantRemoval_load():
    dict1 = {'Tank': {'pollutant': 'P1', 'method': 'ConstantRemoval', 'parameters': {'R': 0.5}}}
    conc = []
    conc1 = []
    flow = []
    flow1 = []
    with Simulation("./inps/model_constantinflow_constanteffluent.inp") as sim:
        CR = waterQuality(sim, dict1)
        Outfall = Nodes(sim)["Outfall"]
        for step in sim:
            CR.updateWQState()
            c = Outfall.pollut_quality
            conc.append(c['P1'])
            flow.append(sim._model.getNodeResult("Outfall",0))
        load = [a*b for a,b in zip(conc,flow)]
        cum_load = np.cumsum(load)
    with Simulation("./inps/model_constantinflow_constanteffluent_constantremoval.inp") as sim:
        Outfall = Nodes(sim)["Outfall"]
        for step in sim:
            c = Outfall.pollut_quality
            conc1.append(c['P1'])
            flow1.append(sim._model.getNodeResult("Outfall",0))
        load1 = [a*b for a,b in zip(conc1,flow1)]
        cum_load1 = np.cumsum(load1)    
    error = (cum_load1[-1]/cum_load[-1])/cum_load1[-1]
    print(error)
    assert error <= 0.03


# CoRemoval
def test_CoRemoval_conc():
    dict1 = {'Tank': {'pollutant': 'P2', 'method': 'ConstantRemoval', 'parameters': {'R': 0.15}},\
        'Tank': {'pollutant': 'P1', 'method': 'CoRemoval', 'parameters': {'R1': 0.75, 'R2': 0.15}}}
    conc_P1 = []
    con_P1 = []
    with Simulation("./inps/model_constantinflow_constanteffluent.inp") as sim:
        CO = waterQuality(sim, dict1)
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            CO.updateWQState()
            c = Tank.pollut_quality
            conc_P1.append(c['P1'])
    with Simulation("./inps/model_constantinflow_constanteffluent_coremoval.inp") as sim:
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            co = Tank.pollut_quality
            con_P1.append(co['P1'])
    error = mse(con_P1, conc_P1, squared=True)
    print(error)
    assert error <= 0.06

def test_CoRemoval_load():
    dict1 = {'Tank': {'pollutant': 'P2', 'method': 'ConstantRemoval', 'parameters': {'R': 0.15}},\
        'Tank': {'pollutant': 'P1', 'method': 'CoRemoval', 'parameters': {'R1': 0.75, 'R2': 0.15}}}
    conc = []
    conc1 = []
    flow = []
    flow1 = []
    with Simulation("./inps/model_constantinflow_constanteffluent.inp") as sim:
        CO = waterQuality(sim, dict1)
        Outfall = Nodes(sim)["Outfall"]
        for step in sim:
            CO.updateWQState()
            c = Outfall.pollut_quality
            conc.append(c['P1'])
            flow.append(sim._model.getNodeResult("Outfall",0))
        load = [a*b for a,b in zip(conc,flow)]
        cum_load = np.cumsum(load)
    with Simulation("./inps/model_constantinflow_constanteffluent_coremoval.inp") as sim:
        Outfall = Nodes(sim)["Outfall"]
        for step in sim:
            c = Outfall.pollut_quality
            conc1.append(c['P1'])
            flow1.append(sim._model.getNodeResult("Outfall",0))
        load1 = [a*b for a,b in zip(conc1,flow1)]
        cum_load1 = np.cumsum(load1)    
    error = (cum_load1[-1]/cum_load[-1])/cum_load1[-1]
    print(error)
    assert error <= 0.03
 

# ConcDependRemoval
def test_ConcDependRemoval_conc():
    dict1 = {'Tank': {'pollutant': 'P1', 'method': 'ConcDependRemoval', 'parameters': {'R_l': 0.50, 'BC': 10.0, 'R_u': 0.75}}}
    conc = []
    con = []
    with Simulation("./inps/model_constantinflow_constanteffluent.inp") as sim:
        CDR = waterQuality(sim, dict1)
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            CDR.updateWQState()
            c = Tank.pollut_quality
            conc.append(c['P1'])
    with Simulation("./inps/model_constantinflow_constanteffluent_concdependent.inp") as sim:
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            co = Tank.pollut_quality
            con.append(co['P1'])
    error = mse(con, conc, squared=True)
    print(error)
    assert error <= 0.06

def test_ConcDependRemoval_load():
    dict1 = {'Tank': {'pollutant': 'P1', 'method': 'ConcDependRemoval', 'parameters': {'R_l': 0.50, 'BC': 10.0, 'R_u': 0.75}}}
    conc = []
    conc1 = []
    flow = []
    flow1 = []
    with Simulation("./inps/model_constantinflow_constanteffluent.inp") as sim:
        CDR = waterQuality(sim, dict1)
        Outfall = Nodes(sim)["Outfall"]
        for step in sim:
            CDR.updateWQState()
            c = Outfall.pollut_quality
            conc.append(c['P1'])
            flow.append(sim._model.getNodeResult("Outfall",0))
        load = [a*b for a,b in zip(conc,flow)]
        cum_load = np.cumsum(load)
    with Simulation("./inps/model_constantinflow_constanteffluent_concdependent.inp") as sim:
        Outfall = Nodes(sim)["Outfall"]
        for step in sim:
            c = Outfall.pollut_quality
            conc1.append(c['P1'])
            flow1.append(sim._model.getNodeResult("Outfall",0))
        load1 = [a*b for a,b in zip(conc1,flow1)]
        cum_load1 = np.cumsum(load1)    
    error = (cum_load1[-1]/cum_load[-1])/cum_load1[-1]
    print(error)
    assert error <= 0.03


# NthOrderReaction
def test_NthOrderReaction_conc():
    dict1 = {'Tank': {'pollutant': 'P1', 'method': 'NthOrderReaction', 'parameters': {'k': 0.01, 'n': 2.0}}}
    conc = []
    con = []
    with Simulation("./inps/model_constantinflow_constanteffluent.inp") as sim:
        NOR = waterQuality(sim, dict1)
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            NOR.updateWQState()
            c = Tank.pollut_quality
            conc.append(c['P1'])
    with Simulation("./inps/model_constantinflow_constanteffluent_nthorderreaction.inp") as sim:
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            co = Tank.pollut_quality
            con.append(co['P1'])
    error = mse(con, conc, squared=True)
    print(error)
    assert error <= 0.06

def test_NthOrderReaction_load():
    dict1 = {'Tank': {'pollutant': 'P1', 'method': 'NthOrderReaction', 'parameters': {'k': 0.01, 'n': 2.0}}}
    conc = []
    conc1 = []
    flow = []
    flow1 = []
    with Simulation("./inps/model_constantinflow_constanteffluent.inp") as sim:
        NOR = waterQuality(sim, dict1)
        Outfall = Nodes(sim)["Outfall"]
        for step in sim:
            NOR.updateWQState()
            c = Outfall.pollut_quality
            conc.append(c['P1'])
            flow.append(sim._model.getNodeResult("Outfall",0))
        load = [a*b for a,b in zip(conc,flow)]
        cum_load = np.cumsum(load)
    with Simulation("./inps/model_constantinflow_constanteffluent_nthorderreaction.inp") as sim:
        Outfall = Nodes(sim)["Outfall"]
        for step in sim:
            c = Outfall.pollut_quality
            conc1.append(c['P1'])
            flow1.append(sim._model.getNodeResult("Outfall",0))
        load1 = [a*b for a,b in zip(conc1,flow1)]
        cum_load1 = np.cumsum(load1)    
    error = (cum_load1[-1]/cum_load[-1])/cum_load1[-1]
    print(error)
    assert error <= 0.03


# kCModel
def test_kCModel_conc():
    dict1 = {'Tank': {'pollutant': 'P1', 'method': 'kCModel', 'parameters': {'k': 0.01, 'C_s': 10.0}}}
    conc = []
    con = []
    with Simulation("./inps/model_constantinflow_constanteffluent.inp") as sim:
        kCM = waterQuality(sim, dict1)
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            kCM.updateWQState()
            c = Tank.pollut_quality
            conc.append(c['P1'])
    with Simulation("./inps/model_constantinflow_constanteffluent_kcmodel.inp") as sim:
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            co = Tank.pollut_quality
            con.append(co['P1'])
    error = mse(con, conc, squared=True)
    print(error)
    assert error <= 0.06

def test_kcModel_load():
    dict1 = {'Tank': {'pollutant': 'P1', 'method': 'kCModel', 'parameters': {'k': 0.01, 'C_s': 10.0}}}
    conc = []
    conc1 = []
    flow = []
    flow1 = []
    with Simulation("./inps/model_constantinflow_constanteffluent.inp") as sim:
        kCM = waterQuality(sim, dict1)
        Outfall = Nodes(sim)["Outfall"]
        for step in sim:
            kCM.updateWQState()
            c = Outfall.pollut_quality
            conc.append(c['P1'])
            flow.append(sim._model.getNodeResult("Outfall",0))
        load = [a*b for a,b in zip(conc,flow)]
        cum_load = np.cumsum(load)
    with Simulation("./inps/model_constantinflow_constanteffluent_kcmodel.inp") as sim:
        Outfall = Nodes(sim)["Outfall"]
        for step in sim:
            c = Outfall.pollut_quality
            conc1.append(c['P1'])
            flow1.append(sim._model.getNodeResult("Outfall",0))
        load1 = [a*b for a,b in zip(conc1,flow1)]
        cum_load1 = np.cumsum(load1)    
    error = (cum_load1[-1]/cum_load[-1])/cum_load1[-1]
    print(error)
    assert error <= 0.03

  
# GravitySettling
def test_GravitySettling_conc():
    dict1 = {'Tank': {'pollutant': 'P1', 'method': 'GravitySettling', 'parameters': {'k': 0.01, 'C_s': 10.0}}}
    conc = []
    con = []
    with Simulation("./inps/model_constantinflow_constanteffluent.inp") as sim:
        GS = waterQuality(sim, dict1)
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            GS.updateWQState()
            c = Tank.pollut_quality
            conc.append(c['P1'])
    with Simulation("./inps/model_constantinflow_constanteffluent_gravsettling.inp") as sim:
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            co = Tank.pollut_quality
            con.append(co['P1'])
        error = mse(con, conc, squared=True)
        print(error)
        assert error <= 0.06

def test_GravitySettling_load():
    dict1 = {'Tank': {'pollutant': 'P1', 'method': 'GravitySettling', 'parameters': {'k': 0.01, 'C_s': 10.0}}}
    conc = []
    conc1 = []
    flow = []
    flow1 = []
    with Simulation("./inps/model_constantinflow_constanteffluent.inp") as sim:
        GS = waterQuality(sim, dict1)
        Outfall = Nodes(sim)["Outfall"]
        for step in sim:
            GS.updateWQState()
            c = Outfall.pollut_quality
            conc.append(c['P1'])
            flow.append(sim._model.getNodeResult("Outfall",0))
        load = [a*b for a,b in zip(conc,flow)]
        cum_load = np.cumsum(load)
    with Simulation("./inps/model_constantinflow_constanteffluent_gravsettling.inp") as sim:
        Outfall = Nodes(sim)["Outfall"]
        for step in sim:
            c = Outfall.pollut_quality
            conc1.append(c['P1'])
            flow1.append(sim._model.getNodeResult("Outfall",0))
        load1 = [a*b for a,b in zip(conc1,flow1)]
        cum_load1 = np.cumsum(load1)    
    error = (cum_load1[-1]/cum_load[-1])/cum_load1[-1]
    print(error)
    assert error <= 0.03


def test_CSTR_load():
    dict1 = {'Tank': {'pollutant': 'P1', 'method': 'CSTR', 'parameters': {'k': -0.2, 'n': 1.0, 'c0': 10.0}}}
    conc = []
    conc1 = []
    flow = []
    flow1 = []
    with Simulation("./inps/model_constantinflow_constanteffluent.inp") as sim:
        CS = waterQuality(sim, dict1)
        Tank = Nodes(sim)["Tank"]
        Valve = Links(sim)["Valve"]
        for index,step in enumerate(sim):
            CS.updateWQState_CSTR(index)
            c = Tank.pollut_quality
            conc.append(c['P1'])
            c1 = Valve.pollut_quality
            conc1.append(c1['P1'])
            flow.append(sim._model.getNodeResult("Tank",0))
            flow1.append(sim._model.getLinkResult("Valve",0))
        load = [a*b for a,b in zip(conc,flow)]
        cum_load = np.cumsum(load)
        load1 = [a*b for a,b in zip(conc1,flow1)]
        cum_load1 = np.cumsum(load1)    
    error = (cum_load1[-1]/cum_load[-1])/cum_load1[-1]
    print(error)
    assert error <= 0.03

def test_CSTR_steadystate():
    dict1 = {'Tank': {'pollutant': 'P1', 'method': 'CSTR', 'parameters': {'k': -0.2, 'n': 1.0, 'c0': 10.0}}}
    conc2 = []
    vol = []
    flow = []
    with Simulation("./inps/model_constantinflow_constanteffluent.inp") as sim:
        Tank = Nodes(sim)["Tank"]
        for index,step in enumerate(sim):
            v = Tank.volume
            vol.append(v)
            q = Tank.total_inflow
            flow.append(q)
    with Simulation("./inps/model_constantinflow_constanteffluent.inp") as sim:
        CS = waterQuality(sim, dict1)
        Tank = Nodes(sim)["Tank"]
        for index,step in enumerate(sim):
            CS.updateWQState_CSTR(index)
            c = Tank.pollut_quality
            conc2.append(c['P1'])
    C_steadystate = dict1['Tank']['parameters']['c0'] /((1 - (dict1['Tank']['parameters']['k']*(np.mean(vol)/np.mean(flow))))**dict1['Tank']['parameters']['n'])
    error = (C_steadystate - conc2[-1])/C_steadystate
    assert error <= 0.06


def test_Phosphorus_load():
    dict1 = {'Tank': {'pollutant': 'P1', 'method': 'Phosphorus', 'parameters': {'B1': 0.0000333, 'Ceq0': 0.0081, 'k': 0.00320, 'L': 0.91, 'A': 100,'E': 0.44}}}
    conc = []
    conc1 = []
    flow = []
    flow1 = []
    with Simulation("./inps/model_constantinflow_constanteffluent.inp") as sim:
        PH = waterQuality(sim, dict1)
        Tank = Nodes(sim)["Tank"]
        Valve = Links(sim)["Valve"]
        for index,step in enumerate(sim):
            PH.updateWQState_CSTR(index)
            c = Tank.pollut_quality
            conc.append(c['P1'])
            c1 = Valve.pollut_quality
            conc1.append(c1['P1'])
            flow.append(sim._model.getNodeResult("Tank",0))
            flow1.append(sim._model.getLinkResult("Valve",0))
        load = [a*b for a,b in zip(conc,flow)]
        cum_load = np.cumsum(load)
        load1 = [a*b for a,b in zip(conc1,flow1)]
        cum_load1 = np.cumsum(load1)    
    error = (cum_load1[-1]/cum_load[-1])/cum_load1[-1]
    print(error)
    assert error <= 0.06


# Test dictionary with multiple assets
def test_MultipleTreatments():
    dict1 = {'Tank1': {'pollutant': 'P1', 'method': 'EventMeanConc', 'parameters': {'C': 5.0}}, 
    'Tank2': {'pollutant': 'P1', 'method': 'EventMeanConc', 'parameters': {'C': 2.0}}}
    conc1 = []
    con1 = []
    conc2 = []
    con2 = []
    with Simulation("./inps/model_twotanks_constantinflow_constanteffluent.inp") as sim:
        EMC = waterQuality(sim, dict1)
        Tank1 = Nodes(sim)["Tank1"]
        Tank2 = Nodes(sim)["Tank2"]
        for step in sim:
            EMC.updateWQState()
            c1 = Tank1.pollut_quality
            conc1.append(c1['P1'])
            c2 = Tank2.pollut_quality
            conc2.append(c2['P1'])
    with Simulation("./inps/model_twotanks_constantinflow_constanteffluent_twotreatments.inp") as sim:
        Tank1 = Nodes(sim)["Tank1"]
        Tank2 = Nodes(sim)["Tank2"]
        for step in sim:
            co1 = Tank1.pollut_quality
            con1.append(co1['P1'])
            co2 = Tank2.pollut_quality
            con2.append(co2['P1'])
    error1 = mse(con1, conc1, squared=True)
    error2 = mse(con2, conc2, squared=True)
    print(error1, error2)
    assert (error1, error2) <= (0.03, 0.03)

    