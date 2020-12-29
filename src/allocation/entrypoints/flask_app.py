from datetime import datetime
from flask import Flask, jsonify, request

from allocation.domain import model, events, commands
from allocation.adapters import orm
from allocation.service_layer import unit_of_work, messagebus
from allocation.service_layer.handlers import InvalidSku
from allocation import views

app = Flask(__name__)
orm.start_mappers()

@app.route('/add_batch', methods=['POST'])
def add_batch():
    eta = request.json['eta']
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    cmd = commands.CreateBatch(
        request.json['ref'], request.json['sku'], request.json['qty'], eta,
    )
    messagebus.handle(cmd, unit_of_work.SqlAlchemyUnitOfWork())

    return 'Ok', 201

@app.route('/allocate', methods=['POST'])
def allocate_endpoint():
    try:
        cmd = commands.Allocate(
            request.json['orderid'],
            request.json['sku'],
            request.json['qty'],
        )
        results = messagebus.handle(cmd, unit_of_work.SqlAlchemyUnitOfWork())
        batchref = results.pop(0)
    except InvalidSku as e:
        return jsonify({'message': str(e)}), 400

    return jsonify({'batchref': batchref}), 201


@app.route('/allocations/<orderid>', methods=['GET'])
def allocations_view_endpoint(orderid):
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    result = views.allocations(orderid, uow)
    if not result:
        return 'not found', 404
    
    return jsonify(result), 200
