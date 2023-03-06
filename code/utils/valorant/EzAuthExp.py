__all__ = (
    "AuthenticationError",
    "EzAuthError",
    "MultifactorError",
    "WaitOvertimeError",
    "RatelimitError",
    "InitError",
    "UnkownError"
)

# 自定义EzAuth异常的基类
class EzAuthError(Exception):
    """Base class for Auth errors."""
    def __init__(self, value=''):
            self.value = value

    def __str__(self):
        return repr(self.value)



class AuthenticationError(EzAuthError):
    """Failed to authenticate."""


class RatelimitError(EzAuthError):
    """Ratelimit error."""


class MultifactorError(EzAuthError):
    """Error related to multi-factor authentication."""

class InitError(EzAuthError):
    """Error related to init EzAuth self value."""


class WaitOvertimeError(EzAuthError):
    """Wait for verify code overtime"""

class UnkownError(EzAuthError):
    """UnkownError"""
