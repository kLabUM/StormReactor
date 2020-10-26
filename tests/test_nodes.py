from wq_toolbox.nodes import Node_Quality
from pyswmm import Simulation, Nodes, Links
import numpy as np
from sklearn.metrics import mean_squared_error as mse
import pytest
import matplotlib.pyplot as plt

"""
SWMM Water Quality Methods:
For each method, check the mean square deviation between the toolbox 
computed concentration and the SWMM computed concentration for the 
entire simulation is below 3%.

For each method, check the percent change between the final outfall load
computed by the toolbox and by SWMM is less than 3%.

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
    dict1 = {'Tank': {0: 5.0}}
    conc = []
    con = []
    with Simulation("./inps/tank_variableinflow_notreatment.inp") as sim:
        EMC = Node_Quality(sim, dict1)
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            EMC.EventMeanConc()
            c = Tank.pollut_quality
            conc.append(c['P1'])
    with Simulation("./inps/tank_variableinflow_emc.inp") as sim:
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            co = Tank.pollut_quality
            con.append(co['P1'])
    error = mse(con, conc)
    print(error)
    assert error <= 0.03

def test_EventMeanConc_load():
    dict1 = {'Tank': {0: 5.0}}
    conc = []
    conc1 = []
    flow = []
    flow1 = []
    with Simulation("./inps/tank_variableinflow_notreatment.inp") as sim:
        EMC = Node_Quality(sim, dict1)
        Outfall = Nodes(sim)["Outfall"]
        for step in sim:
            EMC.EventMeanConc()
            c = Outfall.pollut_quality
            conc.append(c['P1'])
            flow.append(sim._model.getNodeResult("Outfall",0))
        load = [a*b for a,b in zip(conc,flow)]
        cum_load = np.cumsum(load)
    with Simulation("./inps/tank_variableinflow_emc.inp") as sim:
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
    dict1 = {'Tank': {0: 0.5}}
    conc = []
    con = []
    with Simulation("./inps/tank_variableinflow_notreatment.inp") as sim:
        CR = Node_Quality(sim, dict1)
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            CR.ConstantRemoval()
            c = Tank.pollut_quality
            conc.append(c['P1'])
    with Simulation("./inps/tank_variableinflow_constantremoval.inp") as sim:
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            co = Tank.pollut_quality
            con.append(co['P1'])
    error = mse(con, conc[1:])
    print(error)
    assert error <= 0.03

def test_ConstantRemoval_load():
    dict1 = {'Tank': {0: 0.5}}
    conc = []
    conc1 = []
    flow = []
    flow1 = []
    with Simulation("./inps/tank_variableinflow_notreatment.inp") as sim:
        CR = Node_Quality(sim, dict1)
        Outfall = Nodes(sim)["Outfall"]
        for step in sim:
            CR.ConstantRemoval()
            c = Outfall.pollut_quality
            conc.append(c['P1'])
            flow.append(sim._model.getNodeResult("Outfall",0))
        load = [a*b for a,b in zip(conc,flow)]
        cum_load = np.cumsum(load)
    with Simulation("./inps/tank_variableinflow_constantremoval.inp") as sim:
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
    dict1 = {'Tank': {0: [0.75, 0.15]}}
    dict2 = {'Tank': {1: 0.15}}
    conc_P1 = []
    con_P1 = []
    with Simulation("./inps/tank_variableinflow_notreatment2.inp") as sim:
        CO = Node_Quality(sim, dict1)
        CR = Node_Quality(sim, dict2)
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            CR.ConstantRemoval()
            CO.CoRemoval()
            c = Tank.pollut_quality
            conc_P1.append(c['P1'])
    with Simulation("./inps/tank_variableinflow_coremoval.inp") as sim:
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            co = Tank.pollut_quality
            con_P1.append(co['P1'])
    error = mse(con_P1, conc_P1[1:])
    print(error)
    assert error <= 0.03

def test_CoRemoval_load():
    dict1 = {'Tank': {0: [0.75, 0.15]}}
    dict2 = {'Tank': {1: 0.15}}
    conc = []
    conc1 = []
    flow = []
    flow1 = []
    with Simulation("./inps/tank_variableinflow_notreatment.inp") as sim:
        CO = Node_Quality(sim, dict1)
        CR = Node_Quality(sim, dict2)
        Outfall = Nodes(sim)["Outfall"]
        for step in sim:
            CR.ConstantRemoval()
            CO.CoRemoval()
            c = Outfall.pollut_quality
            conc.append(c['P1'])
            flow.append(sim._model.getNodeResult("Outfall",0))
        load = [a*b for a,b in zip(conc,flow)]
        cum_load = np.cumsum(load)
    with Simulation("./inps/tank_variableinflow_coremoval.inp") as sim:
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
    dict1 = {'Tank': {0: [0.50, 10.0, 0.75]}}
    conc = []
    con = []
    with Simulation("./inps/tank_variableinflow_notreatment.inp") as sim:
        CDR = Node_Quality(sim, dict1)
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            CDR.ConcDependRemoval()
            c = Tank.pollut_quality
            conc.append(c['P1'])
    with Simulation("./inps/tank_variableinflow_concdependent.inp") as sim:
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            co = Tank.pollut_quality
            con.append(co['P1'])
    error = mse(con, conc[1:])
    print(error)
    assert error <= 0.03

def test_ConcDependRemoval_load():
    dict1 = {'Tank': {0: [0.50, 10.0, 0.75]}}
    conc = []
    conc1 = []
    flow = []
    flow1 = []
    with Simulation("./inps/tank_variableinflow_notreatment.inp") as sim:
        CDR = Node_Quality(sim, dict1)
        Outfall = Nodes(sim)["Outfall"]
        for step in sim:
            CDR.ConcDependRemoval()
            c = Outfall.pollut_quality
            conc.append(c['P1'])
            flow.append(sim._model.getNodeResult("Outfall",0))
        load = [a*b for a,b in zip(conc,flow)]
        cum_load = np.cumsum(load)
    with Simulation("./inps/tank_variableinflow_concdependent.inp") as sim:
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
    dict1 = {'Tank': {0: [0.01, 2.0]}}
    conc = []
    con = []
    with Simulation("./inps/tank_variableinflow_notreatment.inp") as sim:
        NOR = Node_Quality(sim, dict1)
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            NOR.NthOrderReaction()
            c = Tank.pollut_quality
            conc.append(c['P1'])
    with Simulation("./inps/tank_variableinflow_nthorderreaction.inp") as sim:
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            co = Tank.pollut_quality
            con.append(co['P1'])
    error = mse(con, conc[1:])
    print(error)
    assert error <= 0.03

def test_NthOrderReaction_load():
    dict1 = {'Tank': {0: [0.01, 2.0]}}
    conc = []
    conc1 = []
    flow = []
    flow1 = []
    with Simulation("./inps/tank_variableinflow_notreatment.inp") as sim:
        NOR = Node_Quality(sim, dict1)
        Outfall = Nodes(sim)["Outfall"]
        for step in sim:
            NOR.NthOrderReaction()
            c = Outfall.pollut_quality
            conc.append(c['P1'])
            flow.append(sim._model.getNodeResult("Outfall",0))
        load = [a*b for a,b in zip(conc,flow)]
        cum_load = np.cumsum(load)
    with Simulation("./inps/tank_variableinflow_nthorderreaction.inp") as sim:
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
    dict1 = {'Tank': {0: [0.01, 10.0]}}
    conc = []
    con = []
    with Simulation("./inps/tank_variableinflow_notreatment.inp") as sim:
        kCM = Node_Quality(sim, dict1)
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            kCM.kCModel()
            c = Tank.pollut_quality
            conc.append(c['P1'])
    with Simulation("./inps/tank_variableinflow_kcmodel.inp") as sim:
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            co = Tank.pollut_quality
            con.append(co['P1'])
    error = mse(con, conc[1:])
    print(error)
    assert error <= 0.03

def test_kcModel_load():
    dict1 = {'Tank': {0: [0.01, 10.0]}}
    conc = []
    conc1 = []
    flow = []
    flow1 = []
    with Simulation("./inps/tank_variableinflow_notreatment.inp") as sim:
        kCM = Node_Quality(sim, dict1)
        Outfall = Nodes(sim)["Outfall"]
        for step in sim:
            kCM.kCModel()
            c = Outfall.pollut_quality
            conc.append(c['P1'])
            flow.append(sim._model.getNodeResult("Outfall",0))
        load = [a*b for a,b in zip(conc,flow)]
        cum_load = np.cumsum(load)
    with Simulation("./inps/tank_variableinflow_kcmodel.inp") as sim:
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
    dict1 = {'Tank': {0: [0.01, 10.0]}}
    conc = []
    con = []
    with Simulation("./inps/tank_variableinflow_notreatment.inp") as sim:
        GS = Node_Quality(sim, dict1)
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            GS.GravitySettling()
            c = Tank.pollut_quality
            conc.append(c['P1'])
    with Simulation("./inps/tank_variableinflow_gravsettling.inp") as sim:
        Tank = Nodes(sim)["Tank"]
        for step in sim:
            co = Tank.pollut_quality
            con.append(co['P1'])
        error = mse(con, conc[1:])
        print(error)
        assert error <= 0.03

def test_GravitySettling_load():
    dict1 = {'Tank': {0: [0.01, 10.0]}}
    conc = []
    conc1 = []
    flow = []
    flow1 = []
    with Simulation("./inps/tank_variableinflow_notreatment.inp") as sim:
        GS = Node_Quality(sim, dict1)
        Outfall = Nodes(sim)["Outfall"]
        for step in sim:
            GS.GravitySettling()
            c = Outfall.pollut_quality
            conc.append(c['P1'])
            flow.append(sim._model.getNodeResult("Outfall",0))
        load = [a*b for a,b in zip(conc,flow)]
        cum_load = np.cumsum(load)
    with Simulation("./inps/tank_variableinflow_gravsettling.inp") as sim:
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


# CSTR
def test_CSTR_load():
    dict1 = {'Tank': {0: [-0.2, 1.0, 0.0]}}
    conc = []
    conc1 = []
    flow = []
    flow1 = []
    with Simulation("./inps/tank_constantinflow_notreatment.inp") as sim:
        CS = Node_Quality(sim, dict1)
        Tank = Nodes(sim)["Tank"]
        Valve = Links(sim)["Valve"]
        for index,step in enumerate(sim):
            CS.CSTR_solver(index)
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
    dict1 = {'Tank': {0: [-0.2, 1.0, 0.0]}}
    conc = []
    with Simulation("./inps/tank_constantinflow_notreatment.inp") as sim:
        CS = Node_Quality(sim, dict1)
        Tank = Nodes(sim)["Tank"]
        for index,step in enumerate(sim):
            CS.CSTR_solver(index)
            c = Tank.pollut_quality
            conc.append(c['P1'])
    C_steadystate = 10.0/(1 + (0.2/(5/127)))
    print(C_steadystate)
    error = (C_steadystate - conc[-1])/C_steadystate
    print(error)
    assert error <= 0.03