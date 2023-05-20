import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score


class AIModel:
    def __init__(self):
        self.model = None

    def train(self, data_path):
        plant = pd.read_excel(data_path)
        x = plant.iloc[:, 6:10]
        x.columns = ['temperature', 'humidity', 'light', 'moisture']
        y = plant["water"]
        xtrain, xtest, ytrain, ytest = train_test_split(x, y, random_state=1)
        self.model = GaussianNB()
        self.model.fit(xtrain, ytrain)

        y_model = self.model.predict(xtest)
        print("Initialized the model with an accuracy score of " + str(accuracy_score(ytest, y_model)))

    def predict(self, xnew):
        if self.model is not None:
            return self.model.predict(xnew)
        else:
            print("Model has not been trained yet.")
