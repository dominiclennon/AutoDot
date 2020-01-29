# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 22:10:26 2019

@author: thele
"""
import sys
import json
from Sampler_factory import Paper_sampler
from Investigation.Investigation_factory import Investigation_stage

def tune_with_pygor_from_file(config_file):
    
    with open(config_file) as f:
        configs = json.load(f)
        
    pygor_path = configs.get('path_to_pygor',None)
    if pygor_path is not None:
        sys.path.insert(0,pygor_path)
    import Pygor
    pygor = Pygor.Experiment(xmlip=configs.get('ip',None))
        
    gates = configs['gates']
    plunger_gates = configs['plunger_gates']
    
    chan_no = configs['chan_no']
    
    grouped = any(isinstance(i, list) for i in gates)
    
    if grouped:
        def jump(params,plungers=False):
            
            if plungers:
                labels = plunger_gates
            else:
                labels = gates
            
            for i,gate_group in enumerate(labels):
                pygor.setvals(gate_group,[params[i]]*len(gate_group))
                
            return params
    else:
        def jump(params,plungers=False):
            #print(params)
            if plungers:
                labels = plunger_gates
            else:
                labels = gates
            pygor.setvals(labels,params)
            return params
    def measure():
        cvl = pygor.do0d()[chan_no][0]
        return cvl
    def check():
        return pygor.getvals(plunger_gates)
    
    assert len(gates) == len(configs['general']['origin'])
        
        
    investigation_stage = Investigation_stage(jump,measure,check,configs['investigation'])
        
    tune(jump,measure,investigation_stage,configs)

def tune_from_file(jump,measure,check,config_file):
    with open(config_file) as f:
        configs = json.load(f)
    investigation_stage = Investigation_stage(jump,measure,check,configs['investigation'])
    tune(jump,measure,investigation_stage,configs)
    

def tune(jump,measure,investigation_stage,configs):
    configs['jump'] = jump
    configs['measure'] = measure
    configs['investigation_stage_class'] = investigation_stage
    ps = Paper_sampler(configs)
    for i in range(configs['general']['num_samples']):
        print("============### ITERATION %i ###============"%i)
        results = ps.do_iter()
        for key,item in results.items():
            print("%s:"%(key),item[-1])
    
if __name__ == '__main__':
   pass
   #tune_with_pygor_from_file('tuning_config.json') 
        
        