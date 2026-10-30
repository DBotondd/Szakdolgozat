import unittest
from blockchain import Blockchain, hash_text

class TestBlockchain(unittest.TestCase):
    def test_sha256(self):
        self.assertEqual(hash_text('abc'), 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
    def test_valid(self):
        chain = Blockchain(1)
        chain.add_block('Teszt adat')
        self.assertTrue(chain.validate()[0])
        self.assertEqual(chain.blocks[1].previous_hash, chain.blocks[0].hash)
    def test_tamper(self):
        chain = Blockchain(1)
        chain.add_block('Eredeti')
        chain.tamper(1, 'Hamisított')
        self.assertFalse(chain.validate()[0])
    def test_pow(self):
        chain = Blockchain(2)
        self.assertTrue(all(b.hash.startswith('00') for b in chain.blocks))

if __name__ == '__main__':
    unittest.main()
