"""Oktatási célú, egyszálú blokklánc. Nem kriptovaluta vagy elosztott hálózat."""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import time


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


@dataclass
class Block:
    index: int
    timestamp: str
    data: str
    previous_hash: str
    nonce: int = 0
    hash: str = ''

    def calculate_hash(self) -> str:
        payload = {'index': self.index, 'timestamp': self.timestamp, 'data': self.data,
                   'previous_hash': self.previous_hash, 'nonce': self.nonce}
        serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        return hash_text(serialized)


class Blockchain:
    def __init__(self, difficulty: int = 2):
        if not (0 <= difficulty <= 5):
            raise ValueError('A nehézség 0 és 5 közötti legyen.')
        self.difficulty = difficulty
        self.blocks: list[Block] = []
        self.add_block('Genesis blokk')

    def add_block(self, data: str) -> tuple[Block, int, float]:
        previous_hash = self.blocks[-1].hash if self.blocks else '0' * 64
        block = Block(len(self.blocks), datetime.now(timezone.utc).isoformat(), data, previous_hash)
        target = '0' * self.difficulty
        attempts = 0
        start = time.perf_counter()
        while True:
            attempts += 1
            block.hash = block.calculate_hash()
            if block.hash.startswith(target):
                break
            block.nonce += 1
        elapsed = time.perf_counter() - start
        self.blocks.append(block)
        return block, attempts, elapsed

    def validate(self) -> tuple[bool, str, int | None]:
        target = '0' * self.difficulty
        for i, block in enumerate(self.blocks):
            if block.index != i:
                return False, f'A(z) {i}. blokk indexe hibás.', i
            if block.hash != block.calculate_hash():
                return False, f'A(z) {i}. blokk eltárolt hash-e nem egyezik a tartalom hash-ével.', i
            if not block.hash.startswith(target):
                return False, f'A(z) {i}. blokk nem teljesíti a Proof of Work feltételt.', i
            expected = self.blocks[i - 1].hash if i else '0' * 64
            if block.previous_hash != expected:
                return False, f'A(z) {i}. blokk előző hash-hivatkozása hibás.', i
        return True, 'A blokklánc érvényes.', None

    def tamper(self, index: int, new_data: str) -> None:
        if index < 0 or index >= len(self.blocks):
            raise IndexError('Nincs ilyen blokk.')
        self.blocks[index].data = new_data
