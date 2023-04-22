from pydantic import BaseModel
from hashlib import sha256
import logging
import sys
import json

from extract import Jokes


class Node(BaseModel):

    id: int = 0
    prev_hash: str = ""
    hash: str = ""
    payload: str
    nonce: int = 0
    clown: str = "🤡"
    author: str  # host + port узла, открывшего блок

    def __init__(self, **kvargs) -> None:
        super().__init__(**kvargs)
        prev = kvargs.get('prev')
        if prev:
            logging.info(f"generate Node with prev=\n{prev}")
            self.prev_hash = prev.hash
            self.id = prev.id + 1
        else:
            logging.info("generate first Node")
        if not self.hash:
            self.mine()

    def calc_hash(self) -> str:
        fields = {
            'id': self.id,
            'prev_hash': self.prev_hash,
            'payload': self.payload,
            'nonce': self.nonce,
            'clown': self.clown.encode('utf-8'),
            'author': self.author,
        }

        return str(sha256(str(fields).encode("utf-8")).hexdigest())

    def is_valid(self):
        hash = self.calc_hash()
        return hash.endswith('0'*ClownChain.deep)

    def mine(self) -> None:
        hash = self.calc_hash()

        while (not hash.endswith('0'*ClownChain.deep)):
            self.nonce += 1
            hash = self.calc_hash()
            # logging.info(hash)
        self.hash = hash

    def __str__(self) -> str:
        return json.dumps(super().dict(), indent=2, ensure_ascii=False)


class ClownChain:

    deep = 5

    def __init__(self, host: str, gen_init=False) -> None:
        self.host = host
        self.data = [Node(payload="initial block", author=host)
                     ] if gen_init else []

    def add(self, payload: str) -> Node:
        if len(self.data) == 0:
            raise Exception(
                "There is no initial data, try first to get data from main node")
        num = len(self.data)
        node = Node(payload=payload, author=self.host, prev=self.data[-1])
        # если успели намайнить раньше, чем пришел запрос о добавлении
        if len(self.data) == num:
            self.data.append(node)
        else:
            logging.info('Discard new block')
        return node

    def load(self, nodes: list[Node]):
        self.data = nodes.copy()

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, key):
        return self.data[key]


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    c = ClownChain("localhost", True)
    joke = Jokes()
    for _ in range(2):
        c.add(joke())
    for i in range(len(c)):
        print(c[i])
