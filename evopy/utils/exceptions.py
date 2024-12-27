

class IgnoreException(Exception):
    """
    This is the IgnoreException class.
    This class is a subclass of the Exception class.
    This exception is raised when an individual should be ignored.
    """

    def __init__(self, message):
        """
        This is the constructor of the IgnoreException class.
        This method initializes the exception with a message.
        """
        super().__init__(message)