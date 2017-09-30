# -*- coding: utf-8 -*-
import igo.tagger

from django.conf import settings


class Parser:
    def __init__(self, dic_path=None):
        self.dic_path = dic_path if dic_path else settings.NEOLOGD_DIR
        self.tagger = None

    def load_tagger(self):
        self.tagger = igo.tagger.Tagger(self.dic_path)

    def parse(self, text):
        if not self.tagger:
            self.load_tagger()
        return self.tagger.parse(text)


default_parser = Parser()
