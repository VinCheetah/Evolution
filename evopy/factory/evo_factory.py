class EvoFactory:

    def __init__(self, ):
        self.options = None

    def create(self):
        pass

    def set_options(self, options):
        self.options = options

    def get_options(self):
        return self.options
    
    def set_parameter(self, name, value):
        self.options[name] = value
        
    def get_parameter(self, name):
        return self.options[name]
