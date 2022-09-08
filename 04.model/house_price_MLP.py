import pandas as pd
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import explained_variance_score, mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
import joblib, os
import matplotlib.pyplot as plt
import seaborn as sns

class HousePriceModel:

    def __init__(self, c):
        self.cityname = c
        self.modelpath = f'./{self.cityname}/model_mlp.pkl'
        data=pd.read_csv(f'../03.dataset/{self.cityname}_model_features_clean.csv')
        # 單熱編碼
        data_class = pd.get_dummies(data['鄉鎮市區'])
        data_class.columns = ['鄉鎮市區_' + str(x) for x in data_class.columns]
        data = pd.concat([data, data_class], axis = 1)

        # 刪除資料分類用欄位
        data.insert(data.shape[1], 'y', data['單價元平方公尺'])
        data.drop(['單價元平方公尺', 'Unnamed: 0', 'Unnamed: 0.1', 'Unnamed: 0.2', 
        '鄉鎮市區', 'geometry'],axis=1,inplace=True)

        # 低變異過濾
        data = data.loc[:, data.std() > 0]
        data = data.dropna()
        self.feature_count = data.shape[1]

        # 訓練集 & 測試集
        test_data = data.loc[data['交易年份'] >= 111]
        test_data.to_csv(f'./{self.cityname}/test_data.csv')
        train_data =  data.loc[data['交易年份'] < 111]
        
        # 資料標準化
        self.mean = train_data.mean()
        self.std = train_data.std()
        self.train_data = (train_data-self.mean)/self.std

        
    def trainModel(self):
        X_train = np.array(self.train_data.drop('y', axis='columns'))
        y_train = np.array(self.train_data['y'])

        model_mlp = MLPRegressor(random_state=14,max_iter = 400,activation='relu', hidden_layer_sizes=(int(self.feature_count*1/2),int(self.feature_count*1/4)))
        model_mlp.fit(X_train, y_train)
        mlp_score=model_mlp.score(X_train,y_train)

        joblib.dump(model_mlp, f'./{self.cityname}/model_mlp.pkl')
        print(f'model score: {mlp_score}')

    def testModel(self, testfile):
        if os.path.isfile(self.modelpath):
            test_data = pd.read_csv(f'./{self.cityname}/{testfile}.csv')
            test_data.drop(['Unnamed: 0'],axis=1,inplace=True)
            
            test_data = (test_data - self.mean) / self.std
            X_test = np.array(test_data.drop('y', axis='columns'))
            y_test = np.array(test_data['y'])

            
            model_mlp = joblib.load(f'./{self.cityname}/model_mlp.pkl')
            result = model_mlp.predict(X_test)
            fig = plt.figure(figsize=(10,5))
            residuals = (y_test- result)
            sns.distplot(residuals)
            plt.savefig(f'./{self.cityname}/residuals.png')

            data1 = pd.DataFrame({'origin':y_test * self.std['y'] + self.mean['y'],'predict':result* self.std['y'] + self.mean['y'],
                                'residual':(y_test * self.std['y'] + self.mean['y']) - (result* self.std['y'] + self.mean['y'])})
            percentage_error = np.mean(np.abs(data1['origin'] - data1['predict'])) / np.mean(data1['origin']) * 100
            data1['residual_abs'] = data1['residual'].abs()
            data1['y10'] = data1['origin'] / 10 - data1['residual_abs']
            data1['y20'] = data1['origin'] / 5 - data1['residual_abs']
            data1['y30'] = data1['origin'] / 3.333 - data1['residual_abs']
            data1.loc[data1['y10'] >= 0, 'y10'] = 1
            data1.loc[data1['y10'] < 0 , 'y10'] = 0
            data1.loc[data1['y20'] >= 0, 'y20'] = 1
            data1.loc[data1['y20'] < 0 , 'y20'] = 0
            data1.loc[data1['y30'] >= 0, 'y30'] = 1
            data1.loc[data1['y30'] < 0 , 'y30'] = 0
            

            print(f'=========={self.cityname}==========')
            print(f'預測房價落在實際房價+-10%內的機率為:{round(data1["y10"].mean(),4)*100}%')
            print(f'預測房價落在實際房價+-20%內的機率為:{round(data1["y20"].mean(),4)*100}%')
            print(f'預測房價落在實際房價+-30%內的機率為:{round(data1["y30"].mean(),4)*100}%')
            print("Model Percentage Error: {:.2f}%".format(percentage_error))

            
            print(f"mean_absolute_error: {mean_absolute_error(y_test, result)}")
            print(f"mean_squared_error: {mean_squared_error(y_test, result)}")
            print(f"explained_variance_score: {explained_variance_score(y_test, result)}")
            print(f"r2_score: {r2_score(y_test, result)}")

        else:
            print('模型尚未訓練，請先訓練模型')

    
    def predictPrice(self, lst):
        if os.path.isfile(self.modelpath):
            test_data = pd.read_csv(f'./{self.cityname}/test_data.csv')
            test_data.drop(['Unnamed: 0', 'y'],axis=1,inplace=True)
            predict_data = pd.DataFrame(np.array(lst)).T
            predict_data.columns = test_data.columns
            # print(predict_data)
            
            mean = self.mean.drop(['y'])
            std = self.std.drop(['y'])
            predict_data = np.array((predict_data - mean) / std)
            # print(predict_data)

            model_mlp = joblib.load(f'./{self.cityname}/model_mlp.pkl')
            result = model_mlp.predict(predict_data)
            print(result)
            result = result * self.std['y'] + self.mean['y']
            return result
        else:
            print('模型尚未訓練，請先訓練模型')
