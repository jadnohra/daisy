from param.param_slave import CartesianEngineDummySlave

g_param = CartesianEngineDummySlave()

def set_g_param_instance(inst):
    global g_param
    g_param = inst