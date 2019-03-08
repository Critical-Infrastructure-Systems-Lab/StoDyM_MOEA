import numpy as np
from platypus import Problem, Integer, Subset


def dam_storage_sdr_annual(sluc_a, slco_a, ssi_a, dtl_a, dsc_a, dda_a, dste_a, dnuc_a, csw_kg, s_sg):
     
    """
    This function calculates the annual variations of 
    (a) dams' sediment input, Sediment Trapping Efficiency (STE), and storage capacity;
    (b) catchment's Sediment Delivery Ratio
    """
    
    ssi_tv = np.sum(ssi_a)  # stream sediment input total value (ton)
    ssi_ca = np.copy(ssi_a)  # copied array of stream sediment input
    
    # store the connected order of dams' location
    dlco_a = np.empty(len(dtl_a), dtype=int)
    for i_v1, v1 in enumerate(dtl_a):
        dlco_a[i_v1] = np.array([i_v2 for i_v2, v2 in enumerate(slco_a) if v1 in v2])
    
    # argument sort of dams' stream ID connected order and sorting other data 
    dlco_as = np.argsort(dlco_a) 
    dtl_sa = dtl_a[dlco_as] 
    dsc_sa = dsc_a[dlco_as] 
    dste_sa = dste_a[dlco_as] 
    dnuc_sa = dnuc_a[dlco_as]
    
    dsd_v = 0  # initial value of cumulative sediment deposition in dams
    
    # Store dams' sediment input, storage capacity and STE, and catchmnet's SDR value
    dsi_sa = np.empty(len(dtl_a))
    for i_v1, v1 in enumerate(dtl_sa): 
        v1_suc = sluc_a[v1 - 1]  
        if len(v1_suc) == 0:  # if dam's upstream connection is not found
            v1_dsi = ssi_ca[v1-1]
            dsi_sa[i_v1] = v1_dsi  
            v1_dsd = v1_dsi * dste_sa[i_v1]  
            dsd_v += v1_dsd 
            dsc_sa[i_v1] -= (v1_dsd*csw_kg) / s_sg 
            ssi_ca[v1-1] -= v1_dsd
        else:  # if dam's upstream connection is found
            v1_udc = np.array([v2 for v2 in dtl_sa if v2 in v1_suc and v2 != v1])  
            if len(v1_udc) == 0:  # if upstream dam's upstream segments are not found
                v1_dsi = np.sum(ssi_ca[sluc_a[v1-1] - 1])
                dsi_sa[i_v1] = v1_dsi  
                v1_dsd = v1_dsi * dste_sa[i_v1]  
                dsd_v += v1_dsd  
                dsc_sa[i_v1] -= (v1_dsd*csw_kg) / s_sg  
                ssi_ca[v1-1] = v1_dsi - v1_dsd  
            else:  # if upstream dam's upstream segments are found
                v1_rus = np.concatenate([sluc_a[v3-1] if len(sluc_a[v3-1]) != 0 else np.array([v3]) 
                                         for v3 in v1_udc])  # remove upstream segments
                v1_urus = np.unique(v1_rus) 
                v1_auc = np.setdiff1d(v1_suc, v1_urus)  
                v1_dsi = np.sum(ssi_ca[v1_auc-1]) + np.sum(ssi_ca[dtl_a[dnuc_sa[i_v1]] - 1]) 
                dsi_sa[i_v1] = v1_dsi  
                v1_dsd = v1_dsi * dste_sa[i_v1]
                dsd_v += v1_dsd  
                dsc_sa[i_v1] -= (v1_dsd*csw_kg) / s_sg 
                ssi_ca[v1-1] = v1_dsi - v1_dsd  
    
    # argument sort of dams' stream ID and corresponding sort of other data
    dtl_2as = np.argsort(dtl_sa)
    dsi_a = dsi_sa[dtl_2as] 
    dsc_a = dsc_sa[dtl_2as]  
    dste_a = dam_ste(dsc_a, dda_a) 
    
    # Sediment Delivery Ratio
    sdr_v = (ssi_tv-dsd_v) / ssi_tv
    
    return dsi_a, dsc_a, dste_a, sdr_v  # return the outputs


def dam_ste(dsc_a, dda_a):
    
    """
    This function calculates the dams' Sediment Trapping Efficiency (STE) 
    """
    
    dste_a = 1 - (1 / (1 + ((0.0021*0.1*dsc_a) / dda_a))) 
    
    return dste_a  # return the output


def dam_next_upstream_connection(dtl_a, sluc_a):
    
    """
    This function calculates the next upstream connection of dams
    """
    
    # store the dams' all upstream connection
    duc_a = np.empty(len(dtl_a), dtype=object) 
    for i_v1, v1 in enumerate(dtl_a): 
        v1_sluc = sluc_a[v1-1]
        if len(v1_sluc) != 0: 
            duc_a[i_v1] = np.array([np.asscalar(np.where(dtl_a == v2)[0]) 
                                    for v2 in dtl_a 
                                    if v2 in v1_sluc and v2 != v1])
        else: 
            duc_a[i_v1] = v1_sluc
    
    # store the dams' next upstream connection only
    dnuc_a = np.empty(len(dtl_a), dtype=object) 
    for i_v1, v1 in enumerate(duc_a):  
        if len(v1) == 0:  
            dnuc_a[i_v1] = v1 
        else:  
            v1_uuc = [duc_a[v2] for v2 in v1 if len(duc_a[v2]) != 0]
            if len(v1_uuc) != 0:  
                v1_ucd = np.unique(np.concatenate(v1_uuc)) 
                dnuc_a[i_v1] = np.setdiff1d(v1, v1_ucd) 
            else:      
                dnuc_a[i_v1] = v1 
    
    return dnuc_a  # return the output


def dam_deployment_output(sluc_a, slco_a, fa_a, ssi_a, dtl_a, dda_a, dsc_a, pa_v, ste_tv, dle_max, csw_kg, s_sg):
    
    """
    This function calculates:
    (a) the arrays of dams' annual storage capacity variation
    (b) life expectancy of each dam, 
    (c) array of Sediment Delivery Ratio (SDR) up to the maximum life expectancy of all dams 
    """
    
    did_a = np.array(np.arange(len(dtl_a)), dtype=int)  # array of dams' ID
    dste_a = dam_ste(dsc_a, dda_a)  # array of dams's initial STE
    dnuc_a = dam_next_upstream_connection(dtl_a, sluc_a)  # array of dams' initial next upstream connection
    dfo_a = np.empty(0, dtype=int)  # an empty array to store the order of inactive dam(s)
    
    dscv_l = []  # an empty list to store dams' storage capacity variation
    sdr_a = np.empty(0)  # an empty array to store annual SDR variation
    dsv_m = np.array([dsc_a])  # dams' storage capacity variation matrix with first row as initial value  
    
    # store annual variaton of dams' storage capacity and catchment's SDR
    yr_i = 0  # initial year
    while True:
        yr_i += 1 
        dsi_a, dsc_a, dste_a, sdr_v= dam_storage_sdr_annual(sluc_a, slco_a, ssi_a, 
                                                            dtl_a, dsc_a, dda_a, dste_a, dnuc_a, 
                                                            csw_kg, s_sg)
        dsv_m = np.vstack((dsv_m, dsc_a))
        sdr_a = np.append(sdr_a, sdr_v) 
        if yr_i >= dle_max:
            fdi_a = np.where(dtl_a > 0)[0]
        elif np.any((dsc_a <= 0) | (dste_a < ste_tv)):
            fdi_a = np.where((dsc_a <= 0) | (dste_a < ste_tv))[0]
        else:
            continue
        dfo_a = np.append(dfo_a, did_a[fdi_a])
        [dscv_l.append(dsv_m[:, v1]) for v1 in fdi_a]  
        dsv_m = np.delete(dsv_m, fdi_a, axis=1) 
        did_a = np.delete(did_a, fdi_a)
        dtl_a = np.delete(dtl_a, fdi_a) 
        dsc_a = np.delete(dsc_a, fdi_a) 
        dste_a = np.delete(dste_a, fdi_a)
        dnuc_a = dam_next_upstream_connection(dtl_a, sluc_a)  
        dda_a = dam_drainage_area(fa_a, dtl_a, sluc_a, slco_a, pa_v)
        if len(did_a) == 0:
            break
        else:
            continue
    
    # sorted dams' annual storage variation and life expectancy
    dsv_a = (dscv_l[v1] for v1 in np.argsort(dfo_a)) 
    dpvsv_a = (np.delete(v1, np.where(v1 < 0)[0]) for v1 in dsv_a)  
    dnsv_a = np.array([v1/v1[0] for v1 in dpvsv_a])  
    dle_a = np.array([(len(v1)-1) for v1 in dnsv_a])  

    return dnsv_a, dle_a, sdr_a  # return the outputs


def dam_drainage_area(fa_a, dtl_a, sluc_a, slco_a, pa_v):
    
    """
    This function calculates the dams' initial drainage area 
    based on their locations in the stream path
    """
    
    # store the connected order of dams' location
    dlco_a = np.empty(len(dtl_a), dtype=int)  
    for i_v1, v1 in enumerate(dtl_a):
        dlco_a[i_v1] = np.array([i_v2 for i_v2, v2 in enumerate(slco_a) if v1 in v2])
    
    # argument sort of dams' connected order and sorting other data
    dlco_as = np.argsort(dlco_a)
    dlco_sa = dtl_a[dlco_as]  
    
    # store dams' flow accumulation by dams' stream ID connected order
    dtlfa_sa = np.empty(len(dtl_a))
    for i_v1, v1 in enumerate(dlco_sa): 
        v1_sluc = sluc_a[v1-1]  
        v1_udc = [v2 for v2 in dlco_sa if v2 in v1_sluc and v2 != v1] 
        if len(v1_udc) == 0:   
            dtlfa_sa[i_v1] = fa_a[v1-1] + 1 
        else:  
            v1_udci = [np.asscalar(np.where(dlco_sa == v3)[0]) for v3 in v1_udc]  
            v1_udfa = np.sum([dtlfa_sa[v4] for v4 in v1_udci])   
            dtlfa_sa[i_v1] = (fa_a[v1-1]-v1_udfa) + 1  
    
    # dams drainage area (km^2) according to dams' targeted location 
    dtlfa_a = dtlfa_sa[np.argsort(dlco_sa)]
    dda_a = dtlfa_a * pa_v 
    
    return dda_a  # return the output


class StoDyM(Problem):
    
    def __init__(self, nvars, nobjs, nconstrs, ov_t, oa_t):
        super().__init__(nvars, nobjs, nconstrs)
        
        dv_l, od_l, cs_l, d_no, dle_min, dle_max, dsc_ul, dsc_mult, pa_v, ste_tv, csw_kg, s_sg = ov_t
        sluc_a, slco_a, fa_a, ssi_a = oa_t
        
        # required values
        self.d_no = d_no 
        self.dle_min = dle_min 
        self.dle_max = dle_max  
        self.dsc_ul = dsc_ul 
        self.dsc_mult = dsc_mult
        self.pa_v = pa_v
        self.ste_tv = ste_tv
        self.csw_kg = csw_kg
        self.s_sg = s_sg

        # required array
        self.sluc_a = sluc_a
        self.slco_a = slco_a 
        self.fa_a = fa_a 
        self.ssi_a = ssi_a 

        self.directions[:] = od_l  # objective directions list
        self.constraints[:] = cs_l  # constraint sign list
        
        self.dscdv_i = dv_l[1]  # dams storage capacity decision variable type
        if isinstance(self.dscdv_i, Integer):  # if initial storage capacity decision variable is Integer
            self.types[:self.d_no] = dv_l[0]  # set dams' location 
            self.types[self.d_no:] = dv_l[1]  # set dams' initial storage capacity
        else:  # if initial storage capacity decision variable is Subset
            self.types[:self.d_no] = dv_l[0]  # set dams' location 
            self.types[self.d_no] = dv_l[1]  # set dams' initial storage capacity
            
            
    def evaluate(self, solution):
        
        dtl_a, dtlri_a = np.unique([solution.variables[v1] for v1 in range(self.d_no)], 
                                   return_index=True)  # dam targeted location array
        dda_a = dam_drainage_area(self.fa_a, dtl_a, self.sluc_a, self.slco_a, self.pa_v)  # dam drainage area
        
        if isinstance(self.dscdv_i, Integer):  # if dams initial storage capacity is Integer decision variables
            dsc_a = np.array([self.dsc_mult*solution.variables[v1] 
                               for v1 in range(self.d_no, self.nvars)], dtype=float)[dtlri_a]  # dam initial storage capacity
        else:  # if dams initial storage capacity is Subset decision variables
            dsc_a = np.array(solution.variables[-1], dtype=float)[dtlri_a]  # dam initial storage capacity
        
        dnsv_a, dle_a, sdr_a = dam_deployment_output(self.sluc_a, self.slco_a, self.fa_a, self.ssi_a, 
                                                     dtl_a, dda_a, dsc_a, 
                                                     self.pa_v, self.ste_tv, self.dle_max, 
                                                     self.csw_kg, self.s_sg)  # dam deployment output
        
        c_0 = len(dtl_a) - self.d_no   # constraint of different dam ID
        c_1 = len(np.where(dle_a >= self.dle_min)[0]) - self.d_no  # constraint of minimum dam life expectancy
        c_2 = len(np.where(dle_a > self.dle_max)[0])  # constraint of maximum dam life expectancy
        c_3 = np.sum(dsc_a) - self.dsc_ul  # constraint of dam upper storage limit
        
        # objective list
        if np.amax(dle_a) < self.dle_min:  # if maximum life expectancy is less than the targeted minimum life expectancy
            sd_m = np.array([v1[:np.amin(dle_a)] for v1 in dnsv_a]) 
            sdm_a = np.mean(sd_m, axis=0)   
            sdd_max = np.amax([np.mean(np.power(v1-sdm_a, 2))**0.5 for v1 in sd_m])  
            o_l = [np.mean(dle_a)/self.dle_max, sdd_max, sdr_a[0], sdr_a[-1]] 
        elif np.amax(dle_a) >= self.dle_min and c_1 < 0:  # if all dams do not have the the targeted minimum life expectancy
            sd_m = np.array([v1[:np.amin(dle_a)] for v1 in dnsv_a])  
            sdm_a = np.mean(sd_m, axis=0)  
            sdd_max = np.amax([np.mean(np.power(v1-sdm_a, 2))**0.5 for v1 in sd_m])
            o_l = [np.mean(dle_a)/self.dle_max, sdd_max, sdr_a[0], sdr_a[self.dle_min-1]]
        else:  # if all dams do have the the targeted minimum life expectancy
            sd_m = np.array([v1[:self.dle_min] for v1 in dnsv_a])
            sdm_a = np.mean(sd_m, axis=0) 
            sdd_max = np.amax([np.mean(np.power(v1-sdm_a, 2))**0.5 for v1 in sd_m])
            o_l = [np.mean(dle_a)/self.dle_max, sdd_max, sdr_a[0], sdr_a[self.dle_min-1]]
 
        solution.objectives[:] = o_l  # solution objectives
        solution.constraints[:] = [c_0, c_1, c_2, c_3]  # constraint list