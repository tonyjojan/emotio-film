import json
def test_true(app,client):
    assert 1 == 1

def test_endpt(app,client):
    rv = client.get('/test_endpoint')
    assert b'alive' in rv.data

def test_get_movies(app,client):
    rv = client.get('movies')
    assert b'Rated English Movies' in rv.data


    
