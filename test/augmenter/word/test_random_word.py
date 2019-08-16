import unittest

import nlpaug.augmenter.word as naw
from nlpaug.util import Action


class TestRandom(unittest.TestCase):
    def test_swap(self):
        texts = [
            'The quick brown fox jumps over the lazy dog'
        ]
        aug = naw.RandomWordAug(action=Action.SWAP)

        for text in texts:
            self.assertLess(0, len(text))
            augmented_text = aug.augment(text)

            self.assertNotEqual(text, augmented_text)

        self.assertLess(0, len(texts))

    def test_delete(self):
        texts = [
            'The quick brown fox jumps over the lazy dog'
        ]
        aug = naw.RandomWordAug()

        for text in texts:
            self.assertLess(0, len(text))
            augmented_text = aug.augment(text)

            self.assertNotEqual(text, augmented_text)

        self.assertLess(0, len(texts))

    def test_words_attribute(self):
        text = 'The quick brown fox jumps over the lazy dog'
        words = ['fox', 'over']

        augs = [
            naw.RandomWordAug(action=Action.SWAP, words=words),
            naw.RandomWordAug(action=Action.DELETE, words=words),
        ]

        texts = text.split(' ')
        for aug in augs:
            augmented_text = aug.augment(text)
            augmented_texts = augmented_text.split(' ')

            self.assertEqual(texts[3], 'fox')
            self.assertNotEqual(augmented_texts[3], 'fox')
            self.assertEqual(texts[5], 'over')
            self.assertNotEqual(augmented_texts[5], 'over')
