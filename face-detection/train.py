import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression
from xgboost.sklearn import XGBRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import SGDRegressor
from sklearn.kernel_ridge import KernelRidge
from sklearn.linear_model import ElasticNet
from sklearn.linear_model import BayesianRidge

from sklearn.model_selection import train_test_split,GridSearchCV
from sklearn.metrics import mean_absolute_error, max_error
from sklearn.feature_selection import chi2
from sklearn.feature_selection import SelectKBest
from IPython.display import display
import seaborn as sns

#Read dataset
#silence future warnings
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def preprocess(df : pd.DataFrame):
    # Pre-processing

    df = df.drop(["subDirectory_filePath", "valence", "expression"], axis=1)
    
    corr = df.corr()["valence"].sort_values(ascending=False)
    print(corr)

    X = df.drop(["valence"], axis=1)
    y = df["valence"]

    # TODO: Analyze features

    print("classes\n", y.unique())

    print("\nclass distribution\n", y.value_counts())
    return [X], y

def train_val_test(X_list, y):
    train_val_test = []

    for x in X_list:
        X_data, X_test, y_data, y_test = train_test_split(
            x,
            y,
            test_size=0.1,
            random_state=42,
            #stratify=y # balances labels across the sets
        )

        X_train, X_val, y_train, y_val = train_test_split(
            X_data,
            y_data,
            test_size=(0.2/0.9),  # 20% of the original data
            random_state=42,
            #stratify=y_data
        )

        train_val_test.append([(X_train, y_train), (X_val, y_val), (X_test, y_test)])   
    
    return train_val_test

def train_eval(models, train_val_test):
    # Training
    results = []

    def train_and_eval(model, X_train, y_train, X_test, y_test):
        model.fit(X_train, y_train)
        return eval(model, X_test, y_test)

    def eval(model, X_eval, y_eval):
        predicted_val = model.predict(X_eval)
        return mean_absolute_error(y_eval, predicted_val)
    
    for model in models:
        for i ,(train, val, _) in enumerate(train_val_test):
            acc = train_and_eval(model, train[0], train[1], val[0], val[1])
            train_acc = eval(model, train[0], train[1])
            results.append({
                "model": model,
                "feature_select": i,
                "train_mse": train_acc,
                "eval_mse": acc,
                "max_error": max_error(val[1], model.predict(val[0]))
            })

    return results

if __name__ == "__main__":
    models = [
        DecisionTreeRegressor(),
        SVR(),
        LinearRegression(),
        XGBRegressor(),
        GradientBoostingRegressor(),
        SGDRegressor(),
        KernelRidge(),
        ElasticNet(),
        BayesianRidge()
    ]
    dataset_df = pd.read_csv("DiffusionFER/au_data.csv")
    X_list, y  = preprocess(dataset_df, 'arousal')
    
    train_val_test_sets = train_val_test(X_list, y)

    res = train_eval(models, train_val_test_sets)

    val_y = train_val_test_sets[0][1][1]
    train_y = train_val_test_sets[0][0][1]
    res.append({
        "model": "Naive Regressor",
        "feature_select": 0,
        "train_mse": mean_absolute_error(val_y, np.zeros(val_y.shape)),
        "eval_mse": mean_absolute_error(train_y, np.zeros(train_y.shape)),
        "max_error": 1
    })

    res_df = pd.DataFrame(res)
    res_df.to_csv("train.csv")
