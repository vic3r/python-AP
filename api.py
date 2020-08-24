from requests import request
from model import OrderLine, Batch
import flask
from repository import SqlAlchemyRepository

@flask.route.gubbins
def allocate_endpoint():
    batches = SqlAlchemyRepository.list()
    lines = [OrderLine(
        l['order-id'], l['sku'], l['qty']
    ) for l in request.params]
    allocate(lines, batches)
    session.commit()
    return 201
