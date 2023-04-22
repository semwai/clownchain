from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse, Response
from contextlib import asynccontextmanager
import uvicorn
import argparse
import logging
import sys
import requests
import time
from threading import Thread, Event

from clownchain import ClownChain, Node
from extract import Jokes


def send_to_friends(node: Node):
    for url in app.friends:
        try:
            requests.post(f"http://{url}/notify", json=node.dict())
        except requests.ConnectionError as e:
            logging.error(f"connection error with server {url}: {e}")


def mine():
    joke = Jokes()
    while True:
        if app.event.is_set():
            logging.info('mining - pause')
            app.event.wait()
            logging.info('mining - resume')
        if app.stop.is_set():
            logging.info('mining - stop')
            break
        node = app.clownchain.add(joke())
        send_to_friends(node)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info('start')
    app.thread = Thread(name='mine thread', target=mine)
    app.thread.start()
    app.event = Event()
    app.stop = Event()
    yield
    logging.info('stop')
    app.stop.set()
    app.thread.join()


app = FastAPI(lifespan=lifespan)
app.clownchain: ClownChain = None
app.thread: Thread = None
app.event: Event = None
app.friends: list[int] = []


@app.get('/clownchain')  # , response_model=list[Node])
def get_clownchain():
    return app.clownchain.data


@app.post('/node')
def post_node(payload: str, background_tasks: BackgroundTasks):
    """Ручное добавление ноды"""
    logging.debug(f"start mining for {payload=}")
    new_id = len(app.clownchain.data)
    # background_tasks.add_task(app.clownchain.add, payload)
    node = app.clownchain.add(payload)
    return JSONResponse(node.dict(), status_code=201)


@app.post('/notify')
def notify(node: Node):
    """Получение блока от другого хоста с попыткой записью в свой блокчейн"""
    logging.debug(f"get {node=}")
    valid = node.is_valid()
    if not valid:
        return Response(status_code=400)

    try:
        app.event.set()
        if node.id > app.clownchain.data[-1].id:
            app.clownchain.data.append(node)
    finally:
        app.event.clear()
    return Response(status_code=201)


def get_blockchain(host: str, server: str) -> ClownChain:
    """Получение блокчейна от другого хоста"""
    r = None
    while r is None:
        try:
            r = requests.get(f"http://{server}/clownchain")
        except requests.ConnectionError:
            logging.warning('wait for main server')
            time.sleep(5)
    data = r.json()
    nodes = []
    for d in data:
        n = Node(**d)
        if not n.is_valid():
            raise Exception(f"invalid node {n}")
        nodes.append(n)
    chain = ClownChain(host)
    chain.load(nodes)
    return chain


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=10000)
    parser.add_argument('--server', type=str, default='localhost:10000')
    parser.add_argument('--main', type=bool,
                        required=False, default=False)
    parser.add_argument('--friends', nargs='+', type=str, default=[])
    parser.add_argument('--name', default='localhost')
    parser.add_argument('--deep', default=6, type=int)

    args = parser.parse_args()
    logging.info(args)

    app.friends = args.friends
    ClownChain.deep = args.deep
    if args.main:
        app.clownchain = ClownChain(f"localhost:{args.port}", gen_init=True)
    else:
        app.clownchain = get_blockchain(f"{args.name}", args.server)
    uvicorn.run(app, host='0.0.0.0', port=args.port)
