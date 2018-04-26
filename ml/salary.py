# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import string
# from utilities.mongodb import Mongodb
import urllib
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelBinarizer
from sklearn.metrics import mean_squared_error
# 加载机器学习算法模块
from sklearn.linear_model import LinearRegression  # 线性回归
from sklearn.tree import DecisionTreeRegressor  # 决策树
from sklearn.ensemble import RandomForestRegressor  # 随机森林
from sklearn.model_selection import cross_val_score

JOB_PATH = "../data/csv/"
JOB_FILE_NAME = "jobs.csv"

global cate_features
cate_features = None


# 输出DataFrame时，将全部数据都输出
# pd.set_option('display.max_rows', None)


def load_job_data(job_path=JOB_PATH + JOB_FILE_NAME):
    return pd.read_csv(job_path)


# 定义一些Transformer
class DataFrameSelector(BaseEstimator, TransformerMixin):
    def __init__(self, attr_names):
        self.attr_names = attr_names

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X[self.attr_names]


class ProcessTrainingSet(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        pd.set_option('mode.chained_assignment', None)
        # 去除各个字段的首尾空格
        for prop in list(X):
            X[prop] = X[prop].str.strip()

        # 将city字段，城市的城区删除
        X["city"] = [city.split('·')[0] for city in X["city"]]

        # 将tech中的urlencode字符串解码
        X['tech'] = [urllib.parse.unquote(tech).lower() for tech in X["tech"]]

        # 处理工作经验字段
        X["experience"] = X["experience"].str.replace("经验", "")

        pd.set_option('mode.chained_assignment', 'warn')
        return X


class CategoricalFeatures(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.lbs = {}

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        # 技术分类
        if self.lbs.get("tech") is None:
            self.lbs["tech"] = LabelBinarizer(sparse_output=False)
            one_hot_encoder_tech = self.lbs["tech"].fit_transform(X["tech"])
        else:
            one_hot_encoder_tech = self.lbs["tech"].transform(X["tech"])
        print('============one_hot_encoder_tech.shape', one_hot_encoder_tech.shape)

        # 城市分类
        if self.lbs.get("city") is None:
            self.lbs["city"] = LabelBinarizer(sparse_output=False)
            one_hot_encoder_city = self.lbs["city"].fit_transform(X["city"])
        else:
            one_hot_encoder_city = self.lbs["city"].transform(X["city"])
        print('============one_hot_encoder_city.shape', one_hot_encoder_city.shape)

        # 学历分类
        if self.lbs.get("education") is None:
            self.lbs["education"] = LabelBinarizer(sparse_output=False)
            one_hot_encoder_education = self.lbs["education"].fit_transform(X["education"])
        else:
            one_hot_encoder_education = self.lbs["education"].transform(X["education"])
        print('============one_hot_encoder_education.shape', one_hot_encoder_education.shape)

        # 工作经验分类
        if self.lbs.get("experience") is None:
            self.lbs["experience"] = LabelBinarizer(sparse_output=False)
            one_hot_encoder_experience = self.lbs["experience"].fit_transform(X["experience"])
        else:
            one_hot_encoder_experience = self.lbs["experience"].transform(X["experience"])
        print('============one_hot_encoder_experience.shape', one_hot_encoder_experience.shape)

        return np.c_[X.drop(["tech", "city", "education", "experience"], axis=1),
                     one_hot_encoder_tech,
                     one_hot_encoder_city,
                     one_hot_encoder_education,
                     one_hot_encoder_experience]


def transform_salary(X):
    # 将salary的薪资xxk-yyk，转换成数字，公式为(yy-xx)/2
    pd.set_option('mode.chained_assignment', None)
    X['salary'] = [salary.lower().split('-') for salary in X["salary"]]
    salaries = []
    for salary in X['salary']:
        if len(salary) > 1:
            salary = (int(salary[0].split('k')[0]) + int(salary[1].lower().split('k')[0])) / 2
        else:
            salary = int(salary[0].split('k')[0])
        salaries.append(salary)
    X['salary'] = salaries
    pd.set_option('mode.chained_assignment', 'warn')
    return X


def pre_process(data):
    attris = ["tech", "city", "education", "experience"]
    data = transform_salary(data)
    data_label = data["salary"].copy()
    data_features = data.drop("salary", axis=1)
    global cate_features
    if cate_features is None:
        cate_features = CategoricalFeatures()
    pipeline = Pipeline([
        ("selector", DataFrameSelector(attris)),
        ("process", ProcessTrainingSet()),
        ("label_binarizer", cate_features),
    ])

    return pipeline.fit_transform(data_features), data_label


def split_train_test(data, test_ratio):
    shuffled_indices = np.random.permutation(len(data))
    test_set_size = int(len(data) * test_ratio)
    test_indices = shuffled_indices[:test_set_size]
    train_indices = shuffled_indices[test_set_size:]
    return data.iloc[train_indices], data.iloc[test_indices]


def root_mean_squared_error(estimator, X, y):
    prediction = estimator.predict(X)
    mse = mean_squared_error(y, prediction)
    rmse = np.sqrt(mse)
    return rmse


def glance_at_modles(X, y):
    # 1. 线性回归
    lin_reg = LinearRegression()
    lin_reg.fit(X, y)
    print("===============[RMSE]线性回归：", root_mean_squared_error(lin_reg, X, y))
    check_cross_val_score(lin_reg, X, y)
    # 2. 决策树
    tree_reg = DecisionTreeRegressor()
    tree_reg.fit(X, y)
    print("===============[RMSE]决策树：", root_mean_squared_error(tree_reg, X, y))
    check_cross_val_score(tree_reg, X, y)
    # 3. 随机森林
    forest_reg = RandomForestRegressor()
    forest_reg.fit(X, y)
    print("===============[RMSE]随机森林：", root_mean_squared_error(forest_reg, X, y))
    check_cross_val_score(forest_reg, X, y)
    # 4. 神经网络
    pass


def train_models(X, y):
    forest_reg = RandomForestRegressor()
    forest_reg.fit(X, y)
    return forest_reg


def check_cross_val_score(reg, X, y, scoring='neg_mean_squared_error', cv=10):
    scores = cross_val_score(reg, X, y, scoring=scoring, cv=cv)
    rmse_scores = np.sqrt(-scores)
    # 会输出10个rmse score，将之与整个训练集的rmse进行对比，可以查看是否有过拟合
    print('Scores:', rmse_scores)
    print('Mean:', rmse_scores.mean())
    print('Standard deviation:', rmse_scores.std())


def evaluate_model(esti, X, y):
    prediction = esti.predict(X)
    final_mse = mean_squared_error(y, prediction)
    final_rmse = np.sqrt(final_mse)
    return final_rmse


if __name__ == "__main__":
    data = load_job_data()
    train, test = split_train_test(data, 0.2)

    print("==============预处理训练数据======================")
    # 预处理之后，feature类型为ndarray, label类型为Series
    train_feature, train_label = pre_process(train)
    print("==============预处理测试数据======================")
    test_feature, test_label = pre_process(test)
    # print("============train_feature.shape", train_feature.shape)
    # 查看数据相关性
    # todo: 数据全部为非数值数据，无法直接查看相关性

    # 查看各个模型的性能：
    # glance_at_modles(train_feature, train_label)

    # 训练模型
    print("==============训练模型======================")
    estimator = train_models(train_feature, train_label)

    # 验证模型
    result = evaluate_model(estimator, test_feature, test_label)
    print("======验证模型结果：", result)

    # 进行预测
    print("==============开始预测======================")
    predicted = pd.DataFrame({
        "tech": ["java"],
        "city": ["深圳"],
        "education": ["本科"],
        "experience": ["3-5年"],
    })
    # 训练数据中，将分类数据转换成了数值数据，
    # 但是在进行预测时，数据的维度发生问题。训练数据转换后的shape为[93,]
    # 预测数据转换后为[4,]
    # 解决方法：用转换训练数据时的encoder，去转换预测数据

    # print(cate_features.transform(predicted).shape)
    print(estimator.predict(cate_features.transform(predicted)))
