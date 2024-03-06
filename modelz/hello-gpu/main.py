from mosec import Server, Worker, get_logger
from mosec.mixin import MsgpackMixin
from typing import List

logger = get_logger()


class HelloGpu(MsgpackMixin, Worker):
    def __init__(self):
        logger.info("Initializing")

    def forward(self, data: List[str]) -> List[memoryview]:
        logger.info("Received data: %s", data)

        return [memoryview(b"Hello, " + d.encode("utf-8")) for d in data]


if __name__ == "__main__":
    server = Server()
    server.append_worker(HelloGpu, num=1, max_batch_size=4)
    server.run()
