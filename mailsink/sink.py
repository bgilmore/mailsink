
class Sink(object):

    def __init__(self, size=10):
        self._store = [None for i in range(size)]
        self._subs  = set()

    def subscribe(self, d):
        self._subs.add(d)

    def unsub(self, d):
        self._subs.discard(d)

    def add(self, item):
        self._store.pop()
        self._store.insert(0, item)

        # notify subscribers
        for d in self._subs:
            d.callback(item)

        self._subs.clear()

    def contents(self):
        return [message for message in self._store if message is not None]

    def __iter__(self):
        for i in xrange(len(self._store)):
          yield self._store[i]
    
