class MissingDatabaseSessionError(Exception):
    pass

class VMStartupError(Exception):
    def __init__(self, message="Unspecified Error"):
        self.message = message
    
    def __repr__(self):
        return "<VMStartupError('%s')>" % self.message

class NotARealImplementationError(NotImplementedError):
    """
    To be raised by sample module implementations.
    """
    pass

class NoFreeDevicesException(Exception):
    """
    Raised when a VM is told to mount a disk image on the
    next available device, but no device is available.
    """
    pass

