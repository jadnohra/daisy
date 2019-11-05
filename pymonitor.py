from pyscenario import PyScenario

class PyMonitor:
    def __init__(self):
        pass
    
    def _init(self, scenario):
        self.scenario = scenario
        self.init()
        
    def get_description(self):
        return ''
    
    def init(self, scenario):
        pass
    
    