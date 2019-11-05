from .net_msg import Sender


class CartesianEngineSlave:
    def __init__(self, preset_sample_values, master_ip_port):
        self._preset_sample_values = preset_sample_values
        if master_ip_port is not None:
            self._sender = Sender(master_ip_port)
        else:
            self._sender = None
        
    def _declare_new_sampler(self, name, space, dflt):
        if self._sender is not None:
            object = {'name':name, 'space':space, 'dflt':dflt}
            self._sender.send(object)
        
    def sample(self, name, space, dflt):
        if self._preset_sample_values is not None and \
                name in self._preset_sample_values:
            return self._preset_sample_values[name]
        else:
            self._declare_new_sampler(name, space, dflt)
            return dflt
            
    def sample_i(self, name, space, dflt):
        return int(self.sample(name, space, dflt))
        
    def sample_f(self, name, space, dflt):
        return float(self.sample(name, space, dflt))
        
    def sample_b(self, name, space, dflt):
        return not (self.sample(name, space, str(dflt)).lower() in ['false', '0', 'no'])
            
            
class CartesianEngineDummySlave:
    def sample(self, name, space, dflt):
        return dflt

    def sample_i(self, name, space, dflt):
        return dflt
        
    def sample_f(self, name, space, dflt):
        return dflt
        
    def sample_b(self, name, space, dflt):
        return dflt