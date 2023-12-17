class TXSequence:
    def __init__(self, sequence):
        self.sequence = sequence

    @classmethod
    def create(cls, tx_list):
        pass


class TxSequenceElement:
    def __init__(self, tx, results, prev_hash, hash=None):
        self.tx = tx
        self.results = results
        self.prev_hash = prev_hash
        self.hash = hash

    def get_hash(self):
        pass

    def serialize(self):
        pass
