#!./dev/venv/bin/python

import sys
import datetime
import util.logging as logging
from util.arg import *
from util.module import make_class_instance
from dbg_draw.dbg_draw_3d_app import *

def make_scenario_instance(name_pattern):
    return make_class_instance('py_scenarios', name_pattern, "Scenario")
    
def make_monitor_instance(name_pattern):
    return make_class_instance('py_monitors', name_pattern, "Monitor")

def get_scenario_arg():
    if arg_has('-scenario'):
        return arg_get('-scenario', None)
    else:
        return arg_get_positional(1, None)

def scene_pyscenario_update(sctx):
    scene = sctx['scene']
    if (sctx['frame'] == 0):
        scenario_name_pattern = get_scenario_arg()
        scenario_name, scenario_inst = make_scenario_instance(scenario_name_pattern)
        
        road__module_or_file = scenario_inst.get_map()
        road_params = scenario_inst.get_map_parameters()
        scene_road_update_file(sctx, road__module_or_file, road_params)
        
        scenario_inst._init(scene['coord'])
        logging.info(f"scenario: {scenario_name}")
        logging.info(" " + scenario_inst.get_description())
        
        monitor_names = arg_get('-monitors', '').split(',')
        monitor_names = [x for x in monitor_names if len(x.strip())]
        monitor_insts = []
        for monitor_name_pattern in monitor_names:
            monitor_name, monitor_inst = make_monitor_instance(monitor_name_pattern)
            monitor_inst._init(scenario_inst)
            monitor_insts.append(monitor_inst)
            logging.info(f"monitor: {monitor_name}")
            logging.info(" " + monitor_inst.get_description())
        
        scene['scenario'] = scenario_inst
        scene['monitors'] = monitor_insts
        
        scene['dt'] = 1.0/60.0
        scene['t'] = 0.0
        scene['frame'] = 0
        
    if scene['scenario'] is not None:
        t = scene['frame'] * scene['dt']
        scene['scenario']._step(scene['frame'], t, scene['dt'])
        for monitor in scene['monitors']:
            monitor.step(scene['frame'], t, scene['dt'])
        scene['frame'] = scene['frame'] + 1
    return True
    
def loop_headless():
    sctx = deng.g_scene_context
    start_time = datetime.datetime.now()
    while True:
        sctx['t'] = (datetime.datetime.now()-start_time).total_seconds()
        scene_pyscenario_update(sctx)
        deng.update_live_print(sctx, sctx['t']*1000)
        if sctx['stop_frame'] != -1 and sctx['frame'] == sctx['stop_frame']:
            break
        sctx['frame'] = sctx['frame'] + 1
        sctx['loop_frame'] = sctx['loop_frame']+1

def main():
    if arg_has('-headless'):
        loop_headless()
    else:
        scene_title = get_scenario_arg()
        deng.scene_3d_go(scene_title, scene_pyscenario_update,
                         scene_scenario_draw)

if __name__ == "__main__":
    main()
    