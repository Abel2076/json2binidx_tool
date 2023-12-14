import multiprocessing as mp
import jsonlines
from lm_dataformat import listdir_or_file


def handle_jsonl(jsonl_reader):
    for ob in jsonl_reader:
        yield ob


class Reader:
    def __init__(self, in_path):
        self.in_path = in_path

    def stream_data(self, get_meta=False, threaded=False):
        if not threaded:
            yield from self._stream_data(get_meta)
            return

        q = mp.Queue(1000)
        p = mp.Process(target=self._stream_data_threaded, args=(q, get_meta))
        p.start()
        while p.is_alive():
            res = q.get()
            if res is None: break
            yield res

    def _stream_data_threaded(self, q, get_meta=False):
        for data in self._stream_data(get_meta):
            q.put(data)
        q.put(None)

    def _stream_data(self, get_meta=False, jsonl_key="text"):
        self.f_name = ""
        files = listdir_or_file(self.in_path)
        if not files:
            raise FileNotFoundError(f"No valid file(s) found in {self.in_path}")
        for f in files:
            self.f_name = f

            yield from self.read_jsonl(f)

    def read_jsonl(self, file):
        with jsonlines.open(file) as rdr:
            yield from handle_jsonl(rdr)

