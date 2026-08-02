from abc import ABC, abstractmethod


class AbstractConsultantRepository(ABC):
    @abstractmethod
    async def list_consultants(self, page: int = 1, page_size: int = 20):
        raise NotImplementedError
