from dataclasses import dataclass
import json
import string
import os.path as osp
import pathlib

from PIL import Image

import numpy as np
import pandas as pd

from natasha import Doc, NewsEmbedding, NewsMorphTagger, Segmenter, MorphVocab


def _listify(x):
    if not isinstance(x, (list, tuple)):
        x = list(x)
    return x


@dataclass
class Beer:
    name: str
    img_path: str

    def show(self):
        img = Image.open(self.img_path)
        img.show()


class BeerEmbedding:
    def __init__(self):
        with open(osp.join(pathlib.Path(__file__).parent.parent, 'data/beer_features.json'), 'r') as f:
            self.feature_space = json.load(f)
        self._segmenter = Segmenter()
        self._morph_tagger = NewsMorphTagger(NewsEmbedding())
        self._morph_vocab = MorphVocab()

        self._init_beer_table()
        self._init_lemma()

    def _init_beer_table(self):
        data = pd.read_json(osp.join(pathlib.Path(__file__).parent.parent, 'data/beer_data.json'))
        features = []
        images = []
        names = []
        for key in self.feature_space.keys():
            data[key] = data[key].apply(
                lambda x: list(map(str.lower, x)) if x is not np.nan and x is not None else [])
        for name, row in data.iterrows():
            vec = self.featurize(row)
            if vec.sum() > 15:
                features.append(vec)
                images.append(row['img'])
                names.append(name.replace('-', ' '))
        features = np.vstack(features)
        self._features = features
        self._images = images
        self._names = names

    def _init_lemma(self):
        lemmas = []
        for values in self.feature_space.values():
            for v in values:
                lemmas.append(set(self._preprocess_sentence(v)))
        self._lemmas = lemmas

    def featurize(self, row):
        emb = []
        for k, v in self.feature_space.items():
            arr = np.zeros_like(v, dtype=float)
            values = _listify(row[k])
            for v_ in values:
                if v_ in v:
                    arr[v.index(v_)] = 1
            emb.append(arr)
        emb = np.hstack(emb)
        return emb

    def _preprocess_sentence(self, sentence):
        sentence = sentence.translate(str.maketrans('', '', string.punctuation))
        doc = Doc(sentence)
        doc.segment(self._segmenter)
        doc.tag_morph(self._morph_tagger)
        for token in doc.tokens:
            token.lemmatize(self._morph_vocab)
        tokens = [_.lemma for _ in doc.tokens]
        return tokens

    def match(self, sentence, k=3):
        tokens = self._preprocess_sentence(sentence)
        emb = np.zeros_like(self._features[0])
        for i, feats in enumerate(self._lemmas):
            emb[i] = sum(token == feat for feat in feats for token in tokens) / len(feats)
        emb = np.clip(emb, 0., 1.)
        suggestions = ((emb - self._features) ** 2).sum(1).argpartition(k)[:k]
        return [Beer(self._names[i], self._images[i]) for i in suggestions]
