from deeppavlov import build_model, configs


class SentimentAnalysis:
    def __init__(self):
        self.__model = build_model(configs.classifiers.rusentiment_bert, download=False)

    def get_sentiment(self, sentence):
        return self.__model([sentence])[0]
