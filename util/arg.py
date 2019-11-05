import sys

if (hasattr(sys, 'argv')):
    g_argv = sys.argv
else:
    g_argv = []

g_arg_queried = {}
g_arg_help_on = '-help' in g_argv or '-h' in g_argv or '--h' in g_argv
g_arg_help_arg_count = 0

def print_arg_help():
    global g_arg_help_arg_count
    if (len(g_arg_queried) > g_arg_help_arg_count):
        g_arg_help_arg_count = len(g_arg_queried)
        print ('Help:', ', '.join(g_arg_queried.keys()))

def arg_query(keys):
    if (g_arg_help_on and len(keys) and keys[0] not in g_arg_queried):
        g_arg_queried[keys[0]] = ''

def arg_has(keys):
    if (type(keys) is not list):
        keys = [keys]
    arg_query(keys)
    for i in range(len(keys)):
         if (keys[i] in g_argv):
            return True
    return False
    
def arg_has_key(keys):
    if (type(keys) is not list):
        keys = [keys]
    arg_query(keys)
    for key in keys:
        ki = g_argv.index(key) if key in g_argv else -1
        if (ki >= 0 and ki+1 < len(g_argv)):
            return True
    return False
    
def arg_get(keys, dflt):
    if (type(keys) is not list):
        keys = [keys]
    arg_query(keys)
    for key in keys:
        ki = g_argv.index(key) if key in g_argv else -1
        if (ki >= 0 and ki+1 < len(g_argv)):
            return g_argv[ki+1]
    return dflt
    
def arg_get_positional(i, dflt):
    return sys.argv[i] if i < len(sys.argv) else dflt
    
def arg_geti(i, dflt):
    arg_query(['index: {}'.format(i)])
    if (i >= len(g_argv)):
        return dflt
    return g_argv[i]
