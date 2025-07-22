class ResetResponse:
    """
    Represents a standardized response object for API reset or general operations.
    Used across the web application to return consistent structure.
    """

    def __init__(self, success: bool, message: str = "", data=None):
        """
        Initializes the ResetResponse object.

        :param success: Whether the operation was successful.
        :param message: Optional message providing more context.
        :param data: Optional data payload to include in the response.
        """
        self.success = success
        self.message = message
        self.data = data

    def __repr__(self):
        return f"ResetResponse(success={self.success}, message='{self.message}', data={self.data})"

    def to_dict(self):
        """
        Converts the response to a dictionary format (e.g., for JSON serialization).

        :return: dict representation of the response.
        """
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data
        }

    def set_data(self, data):
        """
        Sets the data payload and returns self for chaining.

        :param data: Data to include in the response.
        :return: self
        """
        self.data = data
        return self

    def set_success(self, success: bool):
        """
        Sets the success flag.

        :param success: True or False
        :return: self
        """
        self.success = success
        return self

    def set_message(self, message: str):
        """
        Sets the message text.

        :param message: Message string.
        :return: self
        """
        self.message = message
        return self

    @staticmethod
    def ok(message: str = "操作成功", data=None):
        """
        Returns a successful ResetResponse.

        :param message: Optional message.
        :param data: Optional data payload.
        :return: ResetResponse instance
        """
        return ResetResponse(success=True, message=message, data=data)

    @staticmethod
    def fail(message: str = "操作失败", data=None):
        """
        Returns a failed ResetResponse.

        :param message: Optional error message.
        :param data: Optional data payload.
        :return: ResetResponse instance
        """
        return ResetResponse(success=False, message=message, data=data)