class DomainError(Exception):
    """Нарушение бизнес-инварианта. HTTP-слой маппит её в 400."""


class InvalidNoteError(DomainError): ...
