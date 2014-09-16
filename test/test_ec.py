import unittest

import pyelliptic as ec


class TestPyellipticSymmetric(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ciphername = "aes-256-cfb"
        cls.secret_key = "YELLOW SUBMARINE"

    def test_symmetric_one_pass(self):
        encrypt, decrypt = 1, 0

        iv = ec.Cipher.gen_IV(self.ciphername)
        enc_cipher = ec.Cipher(
            self.secret_key,
            iv,
            encrypt,
            ciphername=self.ciphername
        )

        plaintext_part1 = "Test plaintext part 1"
        plaintext_part2 = "Test plaintext part 2"
        plaintext = plaintext_part1 + plaintext_part2

        ciphertext_part1 = enc_cipher.update(plaintext_part1)
        ciphertext_part2 = enc_cipher.update(plaintext_part2)
        ciphertext_final = enc_cipher.final()
        ciphertext = "".join((
            ciphertext_part1,
            ciphertext_part2,
            ciphertext_final
        ))

        dec_cipher = ec.Cipher(
            self.secret_key,
            iv,
            decrypt,
            ciphername=self.ciphername
        )

        self.assertEqual(plaintext, dec_cipher.ciphering(ciphertext))


class TestPyellipticAsymmetric(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ecc_curve = "secp256k1"
        cls.alice = ec.ECC(curve=cls.ecc_curve)
        cls.bob = ec.ECC(curve=cls.ecc_curve)
        cls.bob_pubkey = cls.bob.get_pubkey()
        cls.bob_privkey = cls.bob.get_privkey()
        cls.alice_pubkey = cls.alice.get_pubkey()
        cls.data = "YELLOW SUBMARINE"

    def test_asymmetric_enc_dec(self):
        plaintext = "Hello Bob"
        ciphertext = self.alice.encrypt(plaintext, self.bob_pubkey)
        self.assertEqual(plaintext, self.bob.decrypt(ciphertext))

    def test_asymmetric_sing_ver(self):
        signature = self.bob.sign("Hello Alice")

        bob_pubkey = self.bob.get_pubkey()
        self.assertTrue(
            ec.ECC(pubkey=bob_pubkey).verify(signature, "Hello Alice")
        )

    def test_key_agreement(self):
        key1 = self.alice.get_ecdh_key(self.bob_pubkey).encode("hex")
        key2 = self.bob.get_ecdh_key(self.alice_pubkey).encode("hex")
        self.assertEqual(key1, key2)

    def test_curve_mismatch(self):
        agent1 = ec.ECC(curve="sect571r1")
        agent2 = self.alice  # working on another curve
        with self.assertRaises(Exception):
            agent2.get_ecdh_key(agent1.get_pubkey())

    def test_encrypt_is_static(self):
        obj_agent1 = ec.ECC(curve=self.ecc_curve)
        obj_agent2 = ec.ECC(curve='sect283k1')
        cls_agent3 = ec.ECC

        encd1 = obj_agent1.encrypt(self.data, self.bob_pubkey)
        encd2 = obj_agent2.encrypt(self.data, self.bob_pubkey)
        encd3 = cls_agent3.encrypt(self.data, self.bob_pubkey)

        dcd1 = self.bob.decrypt(encd1)
        dcd2 = self.bob.decrypt(encd2)
        dcd3 = self.bob.decrypt(encd3)

        self.assertEqual(dcd1, dcd2)
        self.assertEqual(dcd2, dcd3)


if __name__ == "__main__":
    unittest.main()
