from pyswmm import Simulation, Nodes, Links
import pyswmm.toolkitapi as tka
import numpy as np
from scipy.integrate import ode
from enum import Enum

class ElementType(Enum):
    Nodes = 0
    Links = 1

class waterQuality:
    """
    Water quality module for SWMM

    This class provides all the necessary code to run StormReactor's
    water quality module with a SWMM simulation. 

    Attributes
    __________ 
    config : dict
        dictionary with node/links where water quality methods are to 
        be simulated, the pollutants to simulate, the pollutant water
        quality method to simulate, and the method's parameters.

        example:
        config = {
            '11': {'type': 'node', 'pollutant': 'P1', 'method': 'EventMeanConc', 'parameters': {"C": 10}},
            '5': {'type': 'node', 'pollutant': 'P1', 'method': 'ConstantRemoval', 'parameters': {"R": 5}},
            'Link1': {'type': 'link', 'pollutant': 'P1', 'method': 'EventMeanConc', 'parameters': {"C": 10}}, 
            'Link2': {'type': 'link', 'pollutant': 'P1', 'method': 'ConstantRemoval', 'parameters': {"R": 5}}
            }

    Methods
    _______
    updateWQState
        Updates the pollutant concentration during a SWMM simulation for
        all methods except CSTR.

    updateCSTRWQState
        Updates the pollutant concentration during a SWMM simulation for
        a CSTR.
    """
    
    # Initialize class
    def __init__(self, sim, config):
        self.sim = sim
        self.config = config
        self.start_time = self.sim.start_time
        self.last_timestep = self.start_time
        self.solver = ode(self._CSTR_tank)

        # Water quality methods
        self.method = {
            "EventMeanConc": self._EventMeanConc,
            "ConstantRemoval": self._ConstantRemoval,
            "CoRemoval": self._CoRemoval,
            "ConcDependRemoval": self._ConcDependRemoval,
            "NthOrderReaction": self._NthOrderReaction,
            "kCModel": self._kCModel,
            "GravitySettling": self._GravitySettling,
            #"Erosion": self._Erosion,
            "CSTR": self._CSTRSolver,
            "Phosphorus": self._Phosphorus,
            }


    def updateWQState(self):
        """
        Runs the selected water quality method (except CSTR) and updates
        the pollutant concentration during a SWMM simulation.
        """

        # Parse all the elements and their parameters in the config dictionary
        for asset_ID, asset_info in self.config.items():
            attribute = self.config[asset_ID]['method']
            element_type = self.config[asset_ID]['type']
            if element_type == "node":
                element_type = ElementType.Nodes
            else:
                element_type = ElementType.Links
            # Call the water quality method for each element
            self.method[attribute](asset_ID, self.config[asset_ID]['pollutant'], self.config[asset_ID]['parameters'], element_type)

        #Update timestep after water quality methods are completed
        self.last_timestep = self.sim.current_time      


    def updateWQState_CSTR(self, index):
        """
        Runs the water quality method CSTR only and updates the pollutant 
        concentration during a SWMM simulation.
        """

        # Parse all the elements and their parameters in the config dictionary
        for asset_ID, asset_info in self.config.items():
            attribute = self.config[asset_ID]['method']
            element_type = self.config[asset_ID]['type']
            if element_type == "node":
                element_type = ElementType.Nodes
            else:
                print("CSTR does not work for links.")
            # Call the water quality method for each element
            self.method[attribute](index, asset_ID, self.config[asset_ID]['pollutant'], self.config[asset_ID]['parameters'], element_type)
        
        #Update timestep after water quality methods are completed
        self.last_timestep = self.sim.current_time 


    def _EventMeanConc(self, ID, pollutantID, parameters, element_type):
        """
        Event Mean Concentration Treatment (SWMM Water Quality Manual, 2016)
        Treatment results in a constant concentration.

        Treatment method parameters required:
        C = constant treatment concentration for each pollutant (SI/US: mg/L)
        """

        if element_type == ElementType.Nodes:
            # Set new concentration
            self.sim._model.setNodePollut(ID, pollutantID, parameters["C"])
        else:
            # Set new concentration
            self.sim._model.setLinkPollut(ID, pollutantID, parameters["C"])


    def _ConstantRemoval(self, ID, pollutantID, parameters, element_type):
        """
        CONSTANT REMOVAL TREATMENT (SWMM Water Quality Manual, 2016)
        Treatment results in a constant percent removal.
        
        R = pollutant removal fraction (unitless)
        """
        # Get pollutant index
        pollutant_index = self.sim._model.getObjectIDIndex(tka.ObjectType.POLLUT, pollutantID)

        if element_type == ElementType.Nodes:
            # Get SWMM parameter
            Cin = self.sim._model.getNodePollut(ID, tka.NodePollut.inflowQual.value)[pollutant_index]
            # Calculate new concentration
            Cnew = (1-parameters["R"])*Cin
            # Set new concentration 
            self.sim._model.setNodePollut(ID, pollutantID, Cnew)
        else:
            # Get SWMM parameter
            Cin = self.sim._model.getLinkPollut(ID, tka.LinkPollut.reactorQual.value)[pollutant_index]
            # Calculate new concentration
            Cnew = (1-parameters["R"])*Cin
            # Set new concentration 
            self.sim._model.setLinkPollut(ID, pollutantID, Cnew)


    def _CoRemoval(self, ID, pollutantID, parameters, element_type):
        """
        CO-REMOVAL TREATMENT (SWMM Water Quality Manual, 2016)
        Removal of some pollutant is proportional to the removal of
        some other pollutant.

        R1 = pollutant removal fraction (unitless) 
        R2 = pollutant removal fraction for other pollutant (unitless)
        """

        # Get pollutant index
        pollutant_index = self.sim._model.getObjectIDIndex(tka.ObjectType.POLLUT, pollutantID)

        if element_type == ElementType.Nodes:
            # Get SWMM parameter
            Cin = self.sim._model.getNodePollut(ID, tka.NodePollut.inflowQual.value)[pollutant_index]
            # Calculate new concentration
            Cnew = (1-parameters["R1"]*parameters["R2"])*Cin
            # Set new concentration
            self.sim._model.setNodePollut(ID, pollutantID, Cnew)
        else:
            # Get SWMM parameter
            Cin = self.sim._model.getLinkPollut(ID, tka.LinkPollut.reactorQual.value)[pollutant_index]
            # Calculate new concentration
            Cnew = (1-parameters["R1"]*parameters["R2"])*Cin
            # Set new concentration
            self.sim._model.setLinkPollut(ID, pollutantID, Cnew)


    def _ConcDependRemoval(self, ID, pollutantID, parameters, element_type):
        """
        CONCENTRATION-DEPENDENT REMOVAL (SWMM Water Quality Manual, 2016)
        When higher pollutant removal efficiencies occur with higher 
        influent concentrations.
        
        R_l = lower removal rate (unitless)
        BC  = boundary concentration that determines removal rate (SI/US: mg/L)
        R_u = upper removal rate (unitless)
        """

        parameters = parameters
        # Get pollutant index
        pollutant_index = self.sim._model.getObjectIDIndex(tka.ObjectType.POLLUT, pollutantID)

        if element_type == ElementType.Nodes:
            # Get SWMM parameter
            Cin = self.sim._model.getNodePollut(ID, tka.NodePollut.inflowQual.value)[pollutant_index]
            # Calculate removal
            R = (1-np.heaviside((Cin-parameters["BC"]), 0))\
            *parameters["R_l"]+np.heaviside((Cin\
            -parameters["BC"]),0)*parameters["R_u"]
            # Calculate new concentration
            Cnew = (1-R)*Cin
            # Set new concentration
            self.sim._model.setNodePollut(ID, pollutantID, Cnew)
        else:
            # Get SWMM parameter
            Cin = self.sim._model.getLinkPollut(ID, tka.LinkPollut.reactorQual.value)[pollutant_index]
            # Calculate removal
            R = (1-np.heaviside((Cin-parameters["BC"]), 0))\
            *parameters["R_l"]+np.heaviside((Cin\
            -parameters["BC"]),0)*parameters["R_u"]
            # Calculate new concentration
            Cnew = (1-R)*Cin
            # Set new concentration
            self.sim._model.setLinkPollut(ID, pollutantID, Cnew)


    def _NthOrderReaction(self, ID, pollutantID, parameters, element_type):
            """
            NTH ORDER REACTION KINETICS (SWMM Water Quality Manual, 2016)
            When treatment of pollutant X exhibits n-th order reaction kinetics
            where the instantaneous reaction rate is kC^n.
            
            k   = reaction rate constant (SI: m/hr, US: ft/hr)
            n   = reaction order (first order, second order, etc.) (unitless)
            """

            parameters = parameters
            # Get pollutant index
            pollutant_index = self.sim._model.getObjectIDIndex(tka.ObjectType.POLLUT, pollutantID)

            # Get current time
            current_step = self.sim.current_time
            # Calculate model dt in seconds
            dt = (current_step - self.last_timestep).total_seconds()

            if element_type == ElementType.Nodes:
                # Get SWMM parameter
                C = self.sim._model.getNodePollut(ID, tka.NodePollut.reactorQual.value)[pollutant_index]
                # Calculate treatment
                Cnew = C - (parameters["k"]*(C**parameters["n"])*dt)
                # Set new concentration
                self.sim._model.setNodePollut(ID, pollutantID, Cnew)
            else:
                # Get SWMM parameter
                C = self.sim._model.getLinkPollut(ID, tka.LinkPollut.reactorQual.value)[pollutant_index]
                # Calculate treatment
                Cnew = C - (parameters["k"]*(C**parameters["n"])*dt)
                # Set new concentration
                self.sim._model.setLinkPollut(ID, pollutantID, Cnew)


    def _kCModel(self, ID, pollutantID, parameters, element_type):
        """
        K-C_STAR MODEL (SWMM Water Quality Manual, 2016)
        The first-order model with background concentration made popular by 
        Kadlec and Knight (1996) for long-term treatment performance of wetlands.
        
        k   = reaction rate constant (SI: m/hr, US: ft/hr)
        C_s = constant residual concentration that always remains (SI/US: mg/L)
        """

        parameters = parameters
        # Get pollutant index
        pollutant_index = self.sim._model.getObjectIDIndex(tka.ObjectType.POLLUT, pollutantID)

        if element_type == ElementType.Nodes:
            # Get SWMM parameters
            Cin = self.sim._model.getNodePollut(ID, tka.NodePollut.inflowQual.value)[pollutant_index]
            d = self.sim._model.getNodeResult(ID, tka.NodeResults.newDepth.value)
            hrt = self.sim._model.getNodeResult(ID, tka.NodeResults.hyd_res_time.value)
            # Calculate removal
            if d != 0.0 and Cin != 0.0:
                R = np.heaviside((Cin-parameters["C_s"]), 0)\
                *((1-np.exp(-parameters["k"]*hrt/d))*(1-parameters["C_s"]/Cin))
            else:
                R = 0
            # Calculate new concentration
            Cnew = (1-R)*Cin
            # Set new concentration
            self.sim._model.setNodePollut(ID, pollutantID, Cnew) 
        else:
            print("kCModel does not work for links.")


    def _GravitySettling(self, ID, pollutantID, parameters, element_type):
        """
        GRAVITY SETTLING (SWMM Water Quality Manual, 2016)
        During a quiescent period of time within a storage volume, a fraction
        of suspended particles will settle out.

        k   = reaction rate constant (SI: m/hr, US: ft/hr)
        C_s = constant residual concentration that always remains (SI/US: mg/L)
        """

        parameters = parameters
        # Get pollutant index
        pollutant_index = self.sim._model.getObjectIDIndex(tka.ObjectType.POLLUT, pollutantID)

        # Get current time
        current_step = self.sim.current_time
        # Calculate model dt in seconds
        dt = (current_step - self.last_timestep).total_seconds()
        
        if element_type == ElementType.Nodes:
            # Get SWMM parameters
            Cin = self.sim._model.getNodePollut(ID, tka.NodePollut.inflowQual.value)[pollutant_index]
            Qin = self.sim._model.getNodeResult(ID, tka.NodeResults.totalinflow.value)
            d = self.sim._model.getNodeResult(ID, tka.NodeResults.newDepth.value)
            if d != 0.0:
                # Calculate new concentration
                Cnew = np.heaviside((0.1-Qin), 0)*(parameters["C_s"]\
                +(Cin-parameters["C_s"])*np.exp(-parameters["k"]/d*dt/3600))\
                +(1-np.heaviside((0.1-Qin), 0))*Cin
            else:
                Cnew = np.heaviside((0.1-Qin), 0)*parameters["C_s"]\
                +(Cin-parameters["C_s"])+(1-np.heaviside((0.1-Qin), 0))*Cin
            # Set new concentration
            self.sim._model.setNodePollut(ID, pollutantID, Cnew)
        else:
            # Get SWMM parameters
            C = self.sim._model.getLinkPollut(ID, tka.LinkPollut.reactorQual.value)[pollutant_index]
            Q = self.sim._model.getLinkResult(ID, tka.LinkResults.newFlow.value)
            d = self.sim._model.getLinkResult(ID, tka.LinkResults.newDepth.value)
            if d != 0.0:
                # Calculate new concentration
                Cnew = np.heaviside((0.1-Q), 0)*(parameters["C_s"]\
                +(C-parameters["C_s"])*np.exp(-parameters["k"]/d*dt/3600))\
                +(1-np.heaviside((0.1-Q), 0))*C
            else:
                Cnew = np.heaviside((0.1-Q), 0)*parameters["C_s"]\
                +(C-parameters["C_s"])+(1-np.heaviside((0.1-Q), 0))*C
            # Set new concentration
            self.sim._model.setLinkPollut(ID, pollutantID, Cnew)


    """
    Need to add conduit velocity getter to swmm/pyswmm
    def _Erosion(self, ID, pollutantID, parameters, flag): 
        
        ENGELUND-HANSEN EROSION (1967)
        Engelund and Hansen (1967) developed a procedure for predicting stage-
        discharge relationships and sediment transport in alluvial streams.
        
        w   = channel width (SI: m, US: ft)
        So  = bottom slope (SI: m/m, US: ft/ft)
        Ss  = specific gravity of sediment (for soil usually between 2.65-2.80)
        d50 = mean sediment particle diameter (SI/US: mm)
        d   = depth (SI: m, US: ft)
        qt  = sediment discharge per unit width (SI: kg/m-s, US: lb/ft-s)
        Qt  = sediment discharge (SI: kg/s, US: lb/s)
        

        parameters = parameters

        # Get current time
        current_step = self.sim.current_time
        # Calculate model dt in seconds
        dt = (current_step - self.last_timestep).total_seconds()
        # Updating reference step
        self.last_timestep = current_step

        if self.flag == 0:
            print("Erosion does not work for nodes.")
        else:
            # Get SWMM parameters
            Cin = self.sim._model.getLinkC2(ID, pollutantID)
            Q = self.sim._model.getLinkResult(ID, 0)
            d = self.sim._model.getLinkResult(ID, 1)
            v = self.sim._model.getConduitVelocity(ID)
            
            # Erosion calculations for US units
            if self.sim._model.getSimUnit(0) == "US":
                g = 32.2            # ft/s^2
                ρw = 62.4           # lb/ft^3
                mm_ft = 0.00328     # ft/mm
                lb_mg = 453592      # mg/lb
                L_ft3 = 0.0353      # ft3/L
                if v != 0.0:
                    qt = 0.1*(1/((2*g*parameters["So"]*d)/v**2))*((d\
                    *parameters["So"]/((parameters["Ss"]-1)*parameters["d50"]))\
                    *(1/mm_ft))**(5/2)*parameters["Ss"]*ρw*((parameters["Ss"]-1)\
                    *g*(parameters["d50"]*mm_ft)**3)**(1/2) # lb/ft-s
                    Qt = parameters["w"]*qt       # lb/s
                else:
                    Qt = 0.0
                if Q !=0.0:
                    Cnew = (Qt/Q)*lb_mg*L_ft3   # mg/L
                    Cnew = max(Cin, Cin+Cnew)
                    # Set new concentration
                    self.sim._model.setLinkPollut(ID, pollutantID, Cnew)

            # Erosion calculations for SI units
            else:
                g = 9.81            # m/s^2
                ρw = 1000           # kg/m^3
                mm_m = 0.001        # m/mm
                kg_mg = 1000000     # mg/kg
                L_m3 =  0.001       # m3/L
                if v != 0.0:
                    qt = 0.1*(1/((2*g*parameters["So"]*d)/v**2))*((d\
                    *parameters["So"]/((parameters["Ss"]-1)*parameters["d50"]))\
                    *(1/mm_m))**(5/2)*parameters["Ss"]*ρw*((parameters["Ss"]-1)\
                    *g*(parameters["d50"]*mm_m)**3)**(1/2) # kg/m-s
                    Qt = parameters["w"]*qt       # kg/s
                else:
                    Qt = 0.0
                if Q != 0.0:
                    Cnew = (Qt/Q)*L_m3*kg_mg    # mg/L
                    Cnew = max(Cin, Cin+Cnew)
                    # Set new concentration
                    self.sim._model.setLinkPollut(ID, pollutantID, Cnew)
    """


    def _CSTR_tank(self, t, C, Qin, Cin, Qout, V, k, n):
        """
        UNSTEADY CONTINUOUSLY STIRRED TANK REACTOR (CSTR)
        CSTR is a common model for a chemical reactor. The behavior of a CSTR
        is modeled assuming it is not in steady state. This is because
        outflow, inflow, volume, and concentration are constantly changing.

        NOTE: You do not need to call this method, only the CSTR_solver. 
        CSTR_tank is intitalized in __init__ in Node_Treatment.  
        """
        dCdt = (Qin*Cin - Qout*C)/V + k*C**n
        return dCdt


    def _CSTRSolver(self, index, ID, pollutantID, parameters, element_type):
        """
        UNSTEADY CONTINUOUSLY STIRRED TANK REACTOR (CSTR) SOLVER
        CSTR is a common model for a chemical reactor. The behavior of a CSTR
        is modeled assuming it is not in steady state. This is because
        outflow, inflow, volume, and concentration are constantly changing.
        Therefore, Scipy.Integrate.ode solver is used to solve for concentration.
        
        NOTE: You only need to call this method, not CSTR_tank. CSTR_tank is
        intitalized in __init__ in Node_Treatment.  
        
        k   = reaction rate constant (SI/US: 1/s)
        n   = reaction order (first order, second order, etc.) (unitless)
        c0  = intital concentration inside reactor (SI/US: mg/L)
        """

        # Get current time
        current_step = self.sim.current_time
        # Calculate model dt in seconds
        dt = (current_step - self.last_timestep).total_seconds()
        # Get pollutant index
        pollutant_index = self.sim._model.getObjectIDIndex(tka.ObjectType.POLLUT, pollutantID)

        if element_type == ElementType.Nodes:
            # Get SWMM parameters
            Cin = self.sim._model.getNodePollut(ID, tka.NodePollut.inflowQual.value)[pollutant_index]
            Qin = self.sim._model.getNodeResult(ID, tka.NodeResults.totalinflow.value)
            Qout = self.sim._model.getNodeResult(ID, tka.NodeResults.outflow.value)
            V = self.sim._model.getNodeResult(ID, tka.NodeResults.newVolume.value)

            # Parameterize solver
            self.solver.set_f_params(Qin, Cin, Qout, V, parameters["k"], parameters["n"])
            # Solve ODE
            if index == 0:
                self.solver.set_initial_value(parameters["c0"], 0.0)
                self.solver.integrate(self.solver.t+dt)
            else:
                self.solver.set_initial_value(self.solver.y, self.solver.t)
                self.solver.integrate(self.solver.t+dt)
            # Set new concentration
            self.sim._model.setNodePollut(ID, pollutantID, self.solver.y[0])
        else:
            print("CSTR does not work for links.")


    def _Phosphorus(self, index, ID, pollutantID, parameters, element_type):
        """
        LI & DAVIS BIORETENTION CELL TOTAL PHOSPHOURS MODEL (2016)
        Li and Davis (2016) developed a dissolved and particulate phosphorus
        model for bioretention cells.
    
        B1    = coefficient related to the rate at which Ceq approaches Co (SI/US: 1/s)
        Ceq0  = initial DP or PP equilibrium concentration value for an event (SI/US: mg/L)
        k     = reaction rate constant (SI/US: 1/s)
        L     = depth of soil media (length of pathway) (SI: m, US: ft)
        A     = cross-sectional area (SI: m^2, US: ft^2)
        E     = filter bed porosity (unitless)
        """

        parameters = parameters
        t = 0
        # Get pollutant index
        pollutant_index = self.sim._model.getObjectIDIndex(tka.ObjectType.POLLUT, pollutantID)

        if element_type == ElementType.Nodes:
            # Get SWMM parameters
            Cin = self.sim._model.getNodePollut(ID, tka.NodePollut.inflowQual.value)[pollutant_index]
            Qin = self.sim._model.getNodeResult(ID, tka.NodeResults.totalinflow.value)
            # Time calculations for phosphorus model
            if Qin >= 0.01:
                # Get current time
                current_step = self.sim.current_time
                # Calculate model dt in seconds
                dt = (current_step - self.last_timestep).total_seconds()
                # Accumulate time elapsed since water entered node
                t = t + dt
                # Updating reference step
                self.last_timestep = current_step
                # Calculate new concentration
                Cnew = (Cin*np.exp((-parameters["k"]*parameters["L"]\
                    *parameters["A"]*parameters["E"])/Qin))+(parameters["Ceq0"]\
                    *np.exp(parameters["B1"]*t))*(1-(np.exp((-parameters["k"]\
                    *parameters["L"]*parameters["A"]*parameters["E"])/Qin)))
                # Set new concentration
                self.sim._model.setNodePollut(ID, pollutantID, Cnew)
            else:
                t = 0
        else:
            print("Phosphorus does not work for links.")

