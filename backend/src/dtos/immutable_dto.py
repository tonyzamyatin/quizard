from pydantic import BaseModel


class ImmutableBaseModel(BaseModel):
    """
    Base class for immutable data transfer objects.
    """
    def __setattr__(self, name, value):
        if hasattr(self, name):
            raise TypeError(f"{self.__class__.__name__} is immutable and does not support attribute assignment")
        super().__setattr__(name, value)
