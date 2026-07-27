class ServiceError(Exception):
    """Raised by the service layer to signal an HTTP-mapped failure.

    Carries a client-facing message and the HTTP status code the route should
    return. Routes catch this and respond with jsonify({"error": message}), status.
    """

    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status
