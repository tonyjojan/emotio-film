def test_true(app,client):
    assert 1 == 1

def test_endpt(app,client):
    rv = client.get('/test_endpoint')
    assert b'alive' in rv.data

