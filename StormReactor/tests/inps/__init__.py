# -*- coding: utf-8 -*-
# @Author: Brooke Mason
# @Date:   2020-04-25 14:03:33
# @Last Modified by:   HP
# @Last Modified time: 2021-05-17 11:37:15

"""Main tests for StormReactor."""

# Standard library imports
import os
import sys
DATA_PATH = os.path.abspath(os.path.dirname(__file__))

# Test models paths
model_constantinflow_constanteffluent = os.path.join(DATA_PATH, 'model_constantinflow_constanteffluent.inp')
model_constantinflow_constanteffluent_emc = os.path.join(DATA_PATH, 'model_constantinflow_constanteffluent_emc.inp')
model_constantinflow_constanteffluent_constantremoval = os.path.join(DATA_PATH, 'model_constantinflow_constanteffluent_constantremoval.inp')
model_constantinflow_constanteffluent_coremoval = os.path.join(DATA_PATH, 'model_constantinflow_constanteffluent_coremoval.inp')
model_constantinflow_constanteffluent_concdependent = os.path.join(DATA_PATH, 'model_constantinflow_constanteffluent_concdependent.inp')
model_constantinflow_constanteffluent_nthorderreaction = os.path.join(DATA_PATH, 'model_constantinflow_constanteffluent_nthorderreaction.inp')
model_constantinflow_constanteffluent_kcmodel = os.path.join(DATA_PATH, 'model_constantinflow_constanteffluent_kcmodel.inp')
model_constantinflow_constanteffluent_gravsettling = os.path.join(DATA_PATH, 'model_constantinflow_constanteffluent_gravsettling.inp')
model_twotanks_constantinflow_constanteffluent_twotreatments = os.path.join(DATA_PATH, 'model_twotanks_constantinflow_constanteffluent_twotreatments.inp')
model_twotanks_constantinflow_constanteffluent = os.path.join(DATA_PATH, 'model_twotanks_constantinflow_constanteffluent.inp')
LinkTest_variableinflow = os.path.join(DATA_PATH, 'LinkTest_variableinflow.inp')
LinkTest_variableinflow2 = os.path.join(DATA_PATH, 'LinkTest_variableinflow2.inp')
