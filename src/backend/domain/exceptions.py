class DomainError(Exception):
    """Нарушение бизнес-инварианта. HTTP-слой маппит её в 400."""


class InvalidUserError(DomainError): ...


class InvalidPostError(DomainError): ...


class InvalidCommentError(DomainError): ...


class PostStatusError(DomainError):
    """Действие невозможно в текущем статусе поста. HTTP-слой маппит её в 409."""
