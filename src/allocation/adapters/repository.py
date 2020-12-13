  
import abc
from typing import Set
from allocation.domain import model

class AbstractProductRepository(abc.ABC):

    def __init__(self):
        self.seen = set()

    def add(self, product: model.Product):
        self._add(product)
        self.seen.add(product)
    
    def get(self, sku: str) -> model.Product:
        product = self._get(sku)
        if product:
            self.seen.add(product)
        return product

    @abc.abstractmethod
    def _add(self, product):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, sku) -> model.Product:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, product):
        self.session.add(product)

    def _get(self, sku):
        return self.session.query(model.Product).filter_by(sku=sku).with_for_update().first()
