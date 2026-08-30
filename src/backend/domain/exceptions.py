class DomainError(Exception):
    """A business invariant violation. The HTTP layer maps it to 400."""


class InvalidUserError(DomainError): ...


class InvalidPostError(DomainError): ...


class InvalidCommentError(DomainError): ...


class PostStatusError(DomainError):
    """The action is not allowed in the post's current status. Maps to 409."""
