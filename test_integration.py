import pytest
import subprocess
import time
import requests

from clownchain import Node


def test_alone():
    server = subprocess.Popen(
        ['python', 'app.py', '--port', '10000', '--main', 'True', '--deep', '2'])
    time.sleep(1)
    req = requests.get('http://localhost:10000/clownchain')
    data = req.json()
    server.terminate()
    server.wait()
    assert Node(**data[0]).payload == 'initial block'


def test_many():
    server = subprocess.Popen(['python', 'app.py', '--port', '10000',
                              '--main', 'True', '--deep', '4', '--friends', 'localhost:10001'])
    client = subprocess.Popen(
        ['python', 'app.py', '--port', '10001', '--deep', '4', '--friends', 'localhost:10000'])
    res = 0, 1
    time.sleep(10)
    try:
        res = requests.get('http://localhost:10000/clownchain').json(
        ), requests.get('http://localhost:10001/clownchain').json()
    finally:
        time.sleep(1)
        server.kill()
        server.wait()
        client.terminate()
        client.wait()
    assert res[0] == res[1]
