import config
import requests
import random
from model import Batch

def random_batchref(num) -> Batch:
    return Batch(num)

def random_sku() -> str:
    return str(random.randint(100))

def random_orderid() -> int:
    return random.randint(100)

@pytest.mark.usefixtures('restart_api')
def test_api_returns_allocations(add_stock):
    sku, othersku = random_sku(), random_sku('other')

    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)
    add_stock([
        (laterbatch, sku, 100, '2011-01-02'),
        (earlybatch, sku, 100, '2011-01-01'),
        (otherbatch, othersku, 100, None),
    ])
    data = {'orderid': random_orderid(), 'sku': sku, 'qty': 3}
    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json=data)
    assert r.status_code == 200
    assert r.json()['batchref'] == earlybatch

@pytest.mark.usefixtures('restart_api')
def test_allocations_are_persisted(add_stock):
    sku, othersku = random_sku(), random_sku('other')
    batch1, batch2 = random_batchref(1), random_batchref(2)
    order1, order2 = random_orderid(1), random_orderid(2)
    add_stock([
        (order1, sku, 10, '2011-01-01'),
        (order2, sku, 10, '2011-01-02')
    ])
    line1 = { 'orderid': order1, 'sku': sku, 'qty': 10 }
    line2 = { 'orderid': order2, 'sku': sku, 'qty': 10 }
    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json=line1)
    assert r.status_code == 201
    assert r.json()['batchref'] == batch1

    r = requests.post(f'{url}/allocate', json=line2)
    assert r.status_code == 201
    assert r.json()['batchref'] == batch2

@pytest.mark.usefixtures('restart-api')
def test_400_message_for_out_of_stock(add_stock):
    sku, smalL_batch, large_order = random_sku(), random_batchref(), random_orderid()
    add_stock([
        (smalL_batch, sku, 10, '2011-01-01'),
    ])
    data = {'orderid': large_order, 'sku': sku, 'qty': 20}
    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json=data)
    assert r.status_code == 400
    assert r.json()['message'] == f'Out of stock for sku {sku}'

@pytest.mark.usefixtures('restart-api')
def test_400_message_for_out_of_stock():
    unknown_sku, orderid = random_sku(), random_orderid()
    data = {'orderid': orderid, 'sku': unknown_sku, 'qty': 20}
    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json=data)
    assert r.status_code == 400
    assert r.json()['message'] == f'Invalid sku {unknown_sku}'
