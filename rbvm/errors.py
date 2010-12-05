class MissingDatabaseSessionError(Exception):
    pass

class VMStartupError(Exception):
    def __init__(self, message="Unspecified Error"):
        self.message = message
    
    def __repr__(self):
        return "<VMStartupError('%s')>" % self.message

class NotARealImplementationError(Exception):
    """
    To be raised by sample module implementations.
    """
    pass
