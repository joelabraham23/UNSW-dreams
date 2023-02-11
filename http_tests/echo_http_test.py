import pytest
import requests
import json
from src import config
from src.server import APP
from src.auth import _generate_token
import src.error as er

def test_echo():
    '''
    A simple test to check echo
    '''
    resp = requests.get(config.url + 'echo', params={'data': 'hello'})
    assert json.loads(resp.text) == {'data': 'hello'}
