import random
import math
import numbers

class SamplerFloatRange:
    def __init__(self, range):
        self.range = range
        self.rnd = random.Random(0)

    def sample(self):
        return self.uniform(self.range[0], self.range[1])

    def is_exhausted(self):
        return False

 
class SamplerList:
    def __init__(self, range):
        if range == bool:
            range = [True, False]
        self.range = list(range)
        rnd = random.Random(0)
        rnd.shuffle(self.range)
        self.sampled_count = 0
        
    def sample(self):
        self.sampled_count = min(self.sampled_count + 1, len(self.range))
        ret = self.range[self.sampled_count - 1]
        return ret
        
    def is_exhausted(self):
        return self.sampled_count == len(self.range)


class CartesianEngine:
    class _LazyCartesianProduct:
        def __init__(self, set_sizes):
            self.set_sizes = set_sizes
            self.divs = []
            self.mods = []
            self.maxSize = 1
            self.precompute()
        
        def precompute(self):
            for set_size in self.set_sizes:
                self.maxSize = self.maxSize * set_size
            length = len(self.set_sizes)
            factor = 1
            for i in range((length - 1), -1, -1):
                items = self.set_sizes[i]
                self.divs.insert(0, factor)
                self.mods.insert(0, items)
                factor = factor * items
        
        def combination(self, n):
            ret = []
            for i in range(len(self.set_sizes)):
                ret.append(int(math.floor(n / self.divs[i])) % self.mods[i])
            return ret
            
    class _Sampler:
        def __init__(self, name, rng):
            self.name = name
            if rng == 'bool':
                rng = set([True, False])
            if (isinstance(rng, set) or len(rng) != 2 or 
                    (not all([isinstance(x, numbers.Number) for x in rng]))):
                self.range = list(rng)
                self.set_size = len(self.range)
            else:
                self.range = list(range(rng[0], rng[1]+1))
                self.set_size = len(self.range)
            
        def value(self, index):
            return self.range[index]
            
    def __init__(self):
        self.sampler_names = set()
        self.samplers = []
        self.sampled_count = 0
        self.product_size = 0
        self.rnd = random.Random(0) # does this also work with bigint? It seems it does
    
    def get_param_names(self):
        return [x.name for x in self.samplers]
    
    def add_sampler(self, name, space, dflt):
        if name in self.sampler_names:
            # TODO: check that the space and dflt are consistent
            return
        sampler = self._Sampler(name, space)
        self.samplers.append(sampler)
        self.sampler_names.add(name)
        self.product_size = max(self.product_size, 1) * sampler.set_size # By PEP 0237, we get bignum automatically
    
    def sample(self):
        if self.product_size == 0:
            return None
        if self.sampled_count == 0:
            self.lazy_combs = self._LazyCartesianProduct([x.set_size for x in self.samplers])
        if self.sampled_count == self.product_size: #TODO: we may have duplicate samples!
            return None
        index = self.rnd.randint(0, self.product_size-1)
        comb = self.lazy_combs.combination(index)
        ret = [self.samplers[i].value(comb[i]) for i in range(len(comb))]
        self.sampled_count = self.sampled_count + 1
        return ret

def _test_cart_engine():
    param_engine = CartesianEngine()
    print(param_engine.product_size)
    param_engine.add_sampler('test', [1,10], 7)
    print(param_engine.product_size)
    param_engine.add_sampler('test2', ['a', 'b'], 'a')
    print(param_engine.product_size)
    param_engine.add_sampler('test3', [100,105], 100)
    print(param_engine.product_size)
    param_engine.add_sampler('test4', [100,105,107], 105)
    print(param_engine.product_size)
    print(param_engine.sample())
    print(param_engine.sample())
    print(param_engine.sample())
    print(param_engine.sample())
    print(param_engine.sample())
    print(param_engine.sample())
    print(param_engine.sample())


class ParamEngine:
    class _SamplingPath:
        def __init__(self, sampler, dflt, weight):
            self.sampler = sampler
            self.dflt = dflt
            self.sample_count = 0
            self.weigth = weight
        
        def sample(self):
            if self.sample_count == 0 and self.dflt is not None:
                self.sample_count = self.sample_count + 1
                return self.dflt
            ret = self.sampler.sample()
            self.sample_count = self.sample_count + 1
            return ret
        
    def __init__(self):
        self.sampling_paths = {}
        self.total_weight = 0
        self.rnd = random.Random(0)
        
    def _make_sampler(self, space):
        if isinstance(space, set) or isinstance(space, type) or len(space) != 2:
            return SamplerList(space)
        else:
            if any([isinstance(x, float) for x in space]):
                return SamplerFloatRange(space)
            else:
                return SamplerList(range(space[0], space[1]+1))
    
    def sample(self, path, space, dflt):
        if path not in self.sampling_paths:
            sampler = self._make_sampler(space)
            self.sampling_paths[path] = self._SamplingPath(sampler, dflt, 1)
            self.total_weight = self.total_weight + 1
        self.sampling_paths[path].sample()
    
    def print_params(self):
        for path in self.sampling_paths:
            print(f" {path}")
    
g_param = ParamEngine()
