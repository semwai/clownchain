import pytest
from clownchain import Node, ClownChain

ClownChain.deep = 1


def test_node_genesis():
    n1 = Node(payload='Hello pytest', author='pytest')
    assert n1.prev_hash == ''
    assert n1.clown == '🤡'
    assert n1.is_valid()


def test_node_with_prev():
    n1 = Node(payload='Hello pytest', author='pytest')
    n2 = Node(payload='Hello pytest', author='pytest', prev=n1)
    assert n1.hash == n2.prev_hash
    assert n2.is_valid()


def test_fake_node():
    n1 = Node(payload='Hello pytest', author='pytest', hash='1234')
    assert not n1.is_valid()


def test_same_nodes():
    n1 = Node(payload='Hello pytest', author='pytest')
    n2 = Node(payload='Hello pytest', author='pytest', prev=n1)
    n3 = Node(payload='Hello pytest', author='pytest', prev=n1)
    assert n2 == n3


def test_clownchain_init():
    c1 = ClownChain('localhost')
    c2 = ClownChain('localhost', True)
    assert len(c1) == 0
    assert len(c2) == 1
    assert c2.data[0].payload == 'initial block'


def test_clownchain_error():
    c1 = ClownChain('localhost')
    with pytest.raises(Exception):
        c1.add('error')


def test_clownchain_add():
    c1 = ClownChain('localhost', True)
    c1.add('hello')
    c1.add('world')
    assert c1[1].payload == 'hello'
    assert c1[2].payload == 'world'


def test_clownchain_add():
    c1 = ClownChain('localhost', True)
    c1.add('hello')
    c1.add('world')

    c2 = ClownChain('localhost')
    c2.load(c1.data)
    c1.add('123')
    c2.add('123')
    assert c1.data[-1].hash == c2.data[-1].hash

    c3 = ClownChain('localhost-2')
    c3.load(c1.data)
    c1.add('123')
    c3.add('123')
    assert c1.data[-1].hash != c3.data[-1].hash
