
class ComponentBase():
        
    def __init__(self):
        pass
        
    def add_component(self, name, component):
        if self.has_component(name):
            old_comp = self.get_component(name)
            if hasattr(old_comp, 'unbind'):
                old_comp.unbind(self)
        setattr(self, name, component)
        if hasattr(component, 'bind'):
            component.bind(self)
    
    def has_component(self, name):
        return hasattr(self, name) and getattr(self, name) is not None
        
    def get_component(self, name):
        return getattr(self, name)
