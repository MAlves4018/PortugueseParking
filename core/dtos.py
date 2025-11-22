from dataclasses import dataclass
from typing import List, Optional

# Parallel class representing the Order entity as a DTO. The DTO is used to transfer data between the service and the
# controller layer as it would not be easy to use the Django model directly in the controller layer, especially when the
# model is complex and when we do not want to save the object already in the database and working with not yet saved
# objects is not easy in Django (e.g. the id is not yet set, so we cannot use it, cannot access foreign key objects, ..)
# (limitations due to the Active Record pattern in Django ORM)

@dataclass
class CustomerDTO:
    id: Optional[int]          # None before persistence
    username: str
    email: str
    first_name: str
    last_name: str

    def __str__(self) -> str:
        return self.username
