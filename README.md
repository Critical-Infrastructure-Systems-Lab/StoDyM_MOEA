# StoDyM_MOEA
For a given number of check dams in a catchment, this numerical framework optimizes the dams' location and storage capacity in the catchment's stream path. Please take a look on the StoDyM inputs before read the following inputs required for the Multi-Objective Evolutionary Algorithm (MOEA).

## Requirement 
Python 3.6 and Platypus of Python 3, which is a framework for evolutionary computing in Python (https://github.com/Project-Platypus/Platypus)

## Inputs
* cpn_d: Dictionary of catchments' pixel number
* cdn_d: Dictionary of catchments' dam number
* cdscul_d: Dictionary of upper limit of dams' initial total storage capacity
* Storage capaicty of dams: It can be provided by either Integer (dscdv_i = True) or Subset (dscdv_i = False) class from Platypus
  * cdsci_d: Dictionary of dams' storage capacity in terms of Integer class. The user needs to provide a multiplier of Integer (dsc_mult, default value is 1000) to get the actual dams' storage capacity. It can be adjusted according to the range of Integer and storage capacity. Here, the user cannot set a specific search space of dams' storage capacity. 
  * cdscs_d: Dictionary of dams' storage capacity in terms of Subset class. Here, the user can set a specific search space of dams' storage capacity by providing a list (default is list(range(start, end, step))).
* eps_v: Value of epsilon required for EpsNSGAII (default is 0.001)
* cn_s: Name of catchment
* (o_no, ps_no, fe_no, s_no, cc_no):  Numbers of objectives (o_no), population size (ps_no), function evaluations (fe_no), seed (s_no), and computer core (cc_no)  
* od_l: objective decision list of maximization and minimization in case user change any objective 
* cs_l: constraint list in case user change any constraint
* u_p: array of Utopian point (1 for maximization and 0 for minimization)

Note that each dictionary contains two keys "Shejiagou" and "Majiagou", since the framework is tested on these two catchments. The user can insert arbitraty number of catchments. 

## Outputs
For each combination of algorithm and problem, the numerical framework computes the Pareto-front set from the merged solutions of all seeds and saves the Pareto-front set (sheet_name="Pareto_Front") and simultion time (sheet_name="Time") in excel file. Each row of the "Pareto_Front" sheet represents a Pareo-front solution with the information of 
  * dams' location (DO, D1 etc.)
  * dams' storage capacity (SCO, SC1 etc. in m<sup>3</sup>)
  * intial total storage capacity (ITSC, in m<sup>3</sup>)
  * intial total drainage area as a percentage of the catchment area (ITDA)
  * four objective values of average life expectancy (O-LE), storgae dynamics (O-SD), short-term SDR (O-SDR,ST), and long-term SDR (O-SDR,LT)
  * Life expectancy of each dam (LE0, LE1 etc. in years)
  * Average life expectancy (LE_A) in years
  * Distance from Utopian point (last column)
  
Note that SCN and LEN represent the features of DN dam, where N = 0, 1, 2, ..., n and n is the number of dams  


