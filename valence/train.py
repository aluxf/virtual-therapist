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

from joblib import dump, load

#Read dataset
#silence future warnings
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


"""
Optimization:

    Hyperparameter tuning

    Feature selection

"""

def preprocess(df : pd.DataFrame):
    """
    Preprocesses the given DataFrame by performing the following steps:
    1. Drops the columns "subDirectory_filePath", "arousal", and "expression".
    2. Calculates the correlation of each feature with the "valence" column and prints the results.
    3. Separates the features (X) and the target variable (y).
    4. Prints the unique classes in the target variable.
    5. Prints the class distribution of the target variable.
    
    Args:
        df (pd.DataFrame): The input DataFrame containing the data.
        
    Returns:
        list: A list containing the preprocessed features (X) and the target variable (y).
    """
    df = df.drop(["subDirectory_filePath", "arousal", "expression"], axis=1)
    
    corr = df.corr()["valence"].sort_values(ascending=False)
    print(corr)

    X = df.drop(["valence"], axis=1)
    y = df["valence"]

    # TODO: Analyze features

    print("classes\n", y.unique())

    print("\nclass distribution\n", y.value_counts())
    return [X], y

def train_val_test(X_list, y):
    """
    Splits the data into training, validation, and test sets.

    Args:
        X_list (list): A list of input data arrays.
        y (array-like): The target variable array.

    Returns:
        list: A list containing tuples of the form (X_train, y_train), (X_val, y_val), (X_test, y_test).
    """
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
    """
    Train and evaluate multiple models using the given training, validation, and test data.

    Parameters:
    models (list): A list of models to train and evaluate.
    train_val_test (list): A list of tuples containing the training, validation, and test data.

    Returns:
    list: A list of dictionaries containing the evaluation results for each model.

    """
    # Training
    results = []

    def train_and_eval(model, X_train, y_train, X_test, y_test):
        """
        Train and evaluate a single model.

        Parameters:
        model: The model to train and evaluate.
        X_train: The training data features.
        y_train: The training data labels.
        X_test: The test data features.
        y_test: The test data labels.

        Returns:
        float: The evaluation metric (mean absolute error) for the model on the test data.

        """
        model.fit(X_train, y_train)
        return eval(model, X_test, y_test)

    def eval(model, X_eval, y_eval):
        """
        Evaluate a trained model on the given data.

        Parameters:
        model: The trained model to evaluate.
        X_eval: The evaluation data features.
        y_eval: The evaluation data labels.

        Returns:
        float: The evaluation metric (mean absolute error) for the model on the evaluation data.

        """
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
    X_list, y  = preprocess(dataset_df)
    
    train_val_test_sets = train_val_test(X_list, y)

    res = train_eval(models, train_val_test_sets)

    val_y = train_val_test_sets[0][1][1]
    train_y = train_val_test_sets[0][0][1]
    test_y = train_val_test_sets[0][2][1]
    test_X = train_val_test_sets[0][2][0]

    res.append({
        "model": "Naive Regressor",
        "feature_select": 0,
        "train_mse": mean_absolute_error(val_y, np.zeros(val_y.shape)),
        "eval_mse": mean_absolute_error(train_y, np.zeros(train_y.shape)),
        "max_error": 1
    })

    res_df = pd.DataFrame(res)
    res_df.to_csv("train.csv")

    best_model = models[4]
    print(mean_absolute_error(test_y, best_model.predict(test_X)))
    dump(best_model, "valence_model.joblib")