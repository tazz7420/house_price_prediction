import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from keras.utils.vis_utils import plot_model
from sklearn.metrics import explained_variance_score, mean_absolute_error, mean_squared_error, r2_score
import csv, os
import matplotlib.pyplot as plt

def train(city, district):
    data=pd.read_csv(f'../dataset/{city}_model_features.csv')
    if district == 'all':
        data_class = pd.get_dummies(data['鄉鎮市區'])
        data_class.columns = ['鄉鎮市區_' + str(x) for x in data_class.columns]
        data = pd.concat([data, data_class], axis = 1)
    else:
        data = data.loc[data['鄉鎮市區'] == district]
    f_count = data.shape[1]
    data.insert(f_count, 'y', data['單價元平方公尺'])
    data.drop(['單價元平方公尺'],axis=1,inplace=True)
    data.drop(['Unnamed: 0'],axis=1,inplace=True)
    data.drop(['Unnamed: 0.1'],axis=1,inplace=True)
    data.drop(['鄉鎮市區'],axis=1,inplace=True)
    data.drop(['建物型態'],axis=1,inplace=True)
    data.drop(['geometry'],axis=1,inplace=True)
    
    path = f'{city}'
    if not os.path.isdir(path):
        os.mkdir(path)
    
    path = f'{city}/{district}'
    if not os.path.isdir(path):
        os.mkdir(path)
    
    std = data.std()
    std_df = pd.DataFrame(std)
    std_df.to_csv(f'{city}/{district}/std.csv')
    data = data.loc[:, data.std() > 0]
    test_data111 = data.loc[data['交易年份'] == 111]
    data =  data.loc[data['交易年份'] < 111]
    data = data.dropna()
    
    data = data.sample(frac=1.0)
    data = data.reset_index()
    train_data = data.sample(frac=0.8)
    train_data = train_data.dropna()
    
    feature_count = train_data.shape[1]
    
    val_data = data[~data.index.isin(train_data.index)]
    
    # val_data = data2.sample(frac=0.5)
    # test_data = data2[~data2.index.isin(val_data.index)]
    
    train_data.drop(['index'],axis=1,inplace=True)
    val_data.drop(['index'],axis=1,inplace=True)
    # test_data.drop(['index'],axis=1,inplace=True)
    train_validation_data = pd.concat([train_data, val_data])
    mean = train_validation_data.mean()
    std = train_validation_data.std()
    train_data = (train_data-mean)/std
    val_data = (val_data -mean)/std
    
    X_data = np.array(train_data.drop('y', axis='columns'))
    y_data = np.array(train_data['y'])
    X_val = np.array(val_data.drop('y', axis='columns'))
    y_val = np.array(val_data['y'])
    
    model = tf.keras.Sequential()
    model.add(keras.layers.Dense(feature_count-1, activation='relu', input_shape=(feature_count-2,))) 
    model.add(keras.layers.Dense(int(train_data.shape[1]*2/3), activation='relu'))
    model.add(keras.layers.Dense(int(train_data.shape[1]*1/3), activation='relu'))
    model.add(keras.layers.Dense(1)) 
    model.summary()
    
    model.compile(keras.optimizers.Adam(0.0001),
    loss=keras.losses.MeanSquaredError(),
    metrics=[keras.metrics.MeanAbsoluteError()])
    
    model_mckp=keras.callbacks.ModelCheckpoint(f'{city}/{district}/model-1.h5',monitor='val_mean_absolute_error',save_best_only=True,mode='min')
    
    model_cbk=keras.callbacks.TensorBoard()
    history = model.fit(X_data, y_data,batch_size=10, epochs=100, validation_data=(X_val, y_val),  callbacks=[model_cbk, model_mckp])
    
    plt.plot(history.history['loss'], label='train')
    plt.plot(history.history['val_loss'], label='validation')
    plt.title('MSE')
    plt.ylabel('loss')
    plt.xlabel('epochs')
    plt.legend(loc='best')
    plt.savefig(f'{city}/{district}/MSE.png')
    plt.cla()
    
    plt.plot(history.history['mean_absolute_error'], label='train')
    plt.plot(history.history['val_mean_absolute_error'], label='validation')
    plt.title('MAE')
    plt.ylabel('metrics')
    plt.xlabel('epochs')
    plt.legend(loc='best')
    plt.savefig(f'{city}/{district}/MAE.png')
    plt.cla()
    
    
    
    # test
#     model = keras.models.load_model(f'{city}/{district}/model-1.h5')
#     y_test = np.array(test_data['y'])
#     test_data_output = test_data
#     test_data = (test_data - mean) / std
#     x_test = np.array(test_data.drop('y', axis='columns'))
#     y_t = np.array(test_data['y'])
#     y_pred = model.predict(x_test)
#     y_p = y_pred
#     y_pred = np.reshape(y_pred * std['y'] + mean['y'], y_test.shape)
#     percentage_error = np.mean(np.abs(y_test - y_pred)) / np.mean(y_test) * 100
#     print("Model Percentage Error: {:.2f}%".format(percentage_error))
#     print(f"mean_absolute_error: {mean_absolute_error(y_t, y_p)}")
#     print(f"explained_variance_score: {explained_variance_score(y_t, y_p)}")

#     print(f"mean_squared_error: {mean_squared_error(y_t, y_p)}")
#     print(f"r2_score: {r2_score(y_t, y_p)}")
#     f = open(f'{city}/{district}/Accuracy_Index.txt', 'w')
#     f.write("Model Percentage Error: {:.2f}% \n".format(percentage_error))
#     f.write(f"mean_absolute_error: {mean_absolute_error(y_t, y_p)} \n")
#     f.write(f"explained_variance_score: {explained_variance_score(y_t, y_p)} \n")
#     f.write(f"mean_squared_error: {mean_squared_error(y_t, y_p)} \n")
#     f.write(f"r2_score: {r2_score(y_t, y_p)} \n")
#     f.close()
#     y_test = pd.DataFrame(y_test)
#     y_pred = pd.DataFrame(y_pred)
#     test_data_output.reset_index(drop=True, inplace=True)
#     result = pd.concat([test_data_output, y_pred],axis=1,ignore_index=True)
#     result.to_csv(f'{city}/{district}/result.csv')
    
    # test111
    model = keras.models.load_model(f'{city}/{district}/model-1.h5')
    y_test = np.array(test_data111['y'])
    test_data_output = test_data111
    test_data111 = (test_data111 - mean) / std
    x_test = np.array(test_data111.drop('y', axis='columns'))
    y_t = np.array(test_data111['y'])
    y_pred = model.predict(x_test)
    y_p = y_pred
    y_pred = np.reshape(y_pred * std['y'] + mean['y'], y_test.shape)
    percentage_error = np.mean(np.abs(y_test - y_pred)) / np.mean(y_test) * 100
    print("Model Percentage Error: {:.2f}%".format(percentage_error))
    print(f"mean_absolute_error: {mean_absolute_error(y_t, y_p)}")
    print(f"explained_variance_score: {explained_variance_score(y_t, y_p)}")
    # mean_squared_error
    print(f"mean_squared_error: {mean_squared_error(y_t, y_p)}")
    print(f"r2_score: {r2_score(y_t, y_p)}")

    y_test = pd.DataFrame(y_test)
    y_pred = pd.DataFrame(y_pred)
    
    plt.scatter(y_test, y_pred)
    plt.plot([0,1],[0,1])
    plt.savefig(f'{city}/{district}/plt.png')
    plt.cla()
    
    data1 = pd.DataFrame({'origin':y_test,'predict':y_pred})
    data1.corr()
    
    test_data_output.reset_index(drop=True, inplace=True)
    result = pd.concat([test_data_output, y_pred],axis=1)
    result.to_csv(f'{city}/{district}/111_result.csv')
    
    hit_ratio=pd.read_csv(f'{city}/{district}/111_result.csv')
    hit_ratio['y - 0'] = (hit_ratio['y'] - hit_ratio['0']).abs()
    hit_ratio['y10'] = hit_ratio['y'] / 10 - hit_ratio['y - 0']
    hit_ratio['y20'] = hit_ratio['y'] / 5 - hit_ratio['y - 0']
    hit_ratio['y30'] = hit_ratio['y'] / 3.333 - hit_ratio['y - 0']
    hit_ratio.loc[hit_ratio['y10'] >= 0, 'y10'] = 1
    hit_ratio.loc[hit_ratio['y10'] < 0 , 'y10'] = 0
    hit_ratio.loc[hit_ratio['y20'] >= 0, 'y20'] = 1
    hit_ratio.loc[hit_ratio['y20'] < 0 , 'y20'] = 0
    hit_ratio.loc[hit_ratio['y30'] >= 0, 'y30'] = 1
    hit_ratio.loc[hit_ratio['y30'] < 0 , 'y30'] = 0
    print(f'預測房價落在實際房價+-10%內的機率為:{hit_ratio["y10"].mean()}')
    print(f'預測房價落在實際房價+-20%內的機率為:{hit_ratio["y20"].mean()}')
    print(f'預測房價落在實際房價+-30%內的機率為:{hit_ratio["y30"].mean()}')
    f = open(f'{city}/{district}/111_Accuracy_Index.txt', 'w')
    f.write("Model Percentage Error: {:.2f}% \n".format(percentage_error))
    f.write(f"mean_absolute_error: {mean_absolute_error(y_t, y_p)} \n")
    f.write(f"explained_variance_score: {explained_variance_score(y_t, y_p)} \n")
    f.write(f"mean_squared_error: {mean_squared_error(y_t, y_p)} \n")
    f.write(f"r2_score: {r2_score(y_t, y_p)} \n")
    f.write(f'預測房價落在實際房價+-10%內的機率為:{hit_ratio["y10"].mean()}\n')
    f.write(f'預測房價落在實際房價+-20%內的機率為:{hit_ratio["y20"].mean()}\n')
    f.write(f'預測房價落在實際房價+-30%內的機率為:{hit_ratio["y30"].mean()}\n')
    f.close()
    
if __name__ == '__main__':
    code = input("欲處理的城市簡稱: ")
    dist = input("欲處理的鄉鎮市區: ")
    train(code,dist)