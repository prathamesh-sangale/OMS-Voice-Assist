class OMSDataSourceError(Exception):
    """Raised when the data source cannot be loaded or found."""
    pass

class OMSRecordNotFoundError(Exception):
    """Raised when an order or task cannot be found by its identifier."""
    pass

class OMSDataValidationError(Exception):
    """Raised when data from the repository fails schema validation."""
    pass
