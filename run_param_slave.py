#!./dev/venv/bin/python

import sys
import run_scenario
from pyparam import set_g_param_instance
from param.param_slave import CartesianEngineSlave
import param.param_protocol as protocol


def main():
    if protocol.k_arg_capture in sys.argv:
        ip_port = ('localhost', 4997)
        set_g_param_instance(CartesianEngineSlave(None, ip_port))
        run_scenario.main()
    else:
        prefix = protocol.k_arg_par_prefix
        preset_params = {}
        for arg_i, arg in enumerate(sys.argv):
            if arg.startswith(prefix):
                key = arg[len(prefix):]
                val = sys.argv[arg_i+1]
                preset_params[key] = val
        set_g_param_instance(CartesianEngineSlave(preset_params, None))
        run_scenario.main()
    

if __name__ == "__main__":
    main()