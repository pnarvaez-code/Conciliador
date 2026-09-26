from .ports import Port
class UnifiedPort(Port):
    name = "unified"
    def __init__(self, *ports): self.ports = ports
    def fetch(self):
        result = []
        for port in self.ports: result.extend(port.fetch())
        return result
