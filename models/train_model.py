import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from keras.utils.vis_utils import plot_model
from sklearn.metrics import explained_variance_score, mean_absolute_error, mean_squared_error, r2_score
import csv, pydot, graphviz, os
import matplotlib.pyplot as plt

def train(city, district, district_eng):
    data=pd.read_csv(f'../dataset/{city}_model_features.csv')
    data = data.loc[data['鄉鎮市區'] == district]
    data.insert(93, 'y', data['單價元平方公尺'])
    data.drop(['單價元平方公尺'],axis=1,inplace=True)
    data.drop(['Unnamed: 0'],axis=1,inplace=True)
    data.drop(['Unnamed: 0.1'],axis=1,inplace=True)
    data.drop(['鄉鎮市區'],axis=1,inplace=True)
    data.drop(['建物型態'],axis=1,inplace=True)
    data.drop(['車位類別'],axis=1,inplace=True)
    data.drop(['geometry'],axis=1,inplace=True)
    
    path = f'{city}_{district_eng}'
    if not os.path.isdir(path):
        os.mkdir(path)
    
    std = data.std()
    std_df = pd.DataFrame(std)
    std_df.to_csv(f'{city}_{district_eng}/{city}_{district_eng}_std.csv')
    data = data.loc[:, data.std() > 0]
    
    data = data.sample(frac=1.0)
    data = data.reset_index()
    train_data = data.sample(frac=0.8)
    
    feature_count = train_data.shape[1]
    
    data2 = data[~data.index.isin(train_data.index)]
    
    val_data = data2.sample(frac=0.5)
    test_data = data2[~data2.index.isin(val_data.index)]
    
    train_data.drop(['index'],axis=1,inplace=True)
    val_data.drop(['index'],axis=1,inplace=True)
    test_data.drop(['index'],axis=1,inplace=True)
    train_validation_data = pd.concat([train_data, val_data])
    mean = train_validation_data.mean()
    std = train_validation_data.std()
    train_data = (train_data-mean)/std
    val_data = (val_data -mean)/std
    
    X_data = np.array(train_data[train_data.columns[0:feature_count]])
    y_data = np.array(train_data[train_data.columns[-1]]).reshape(len(train_data),1)
    X_val = np.array(val_data[val_data.columns[0:feature_count]])
    y_val = np.array(val_data[val_data.columns[-1]]).reshape(len(val_data),1)
    
    model = tf.keras.Sequential()
    model.add(keras.layers.Dense(feature_count-1, activation='relu', input_shape=(feature_count-1,))) 
    model.add(keras.layers.Dense(int(train_data.shape[1]*2/3), activation='relu'))
    model.add(keras.layers.Dense(1)) 
    
    model.compile(keras.optimizers.Adam(0.0001),
    loss=keras.losses.MeanSquaredError(),
    metrics=[keras.metrics.MeanAbsoluteError()])
    
    model_mckp=keras.callbacks.ModelCheckpoint(f'{city}_{district_eng}/{city}_{district_eng}_model-1.h5',monitor='val_mean_absolute_error',save_best_only=True,mode='min')
    
    model_cbk=keras.callbacks.TensorBoard()
    history = model.fit(X_data, y_data,batch_size=20, epochs=200, validation_data=(X_val, y_val),  callbacks=[model_cbk, model_mckp])
    
    plt.plot(history.history['loss'], label='train')
    plt.plot(history.history['val_loss'], label='validation')
    plt.title('MSE')
    plt.ylabel('loss')
    plt.xlabel('epochs')
    plt.legend(loc='best')
    plt.savefig(f'{city}_{district_eng}/{city}_{district_eng}_MSE.png')
    plt.cla()
    
    plt.plot(history.history['mean_absolute_error'], label='train')
    plt.plot(history.history['val_mean_absolute_error'], label='validation')
    plt.title('MAE')
    plt.ylabel('metrics')
    plt.xlabel('epochs')
    plt.legend(loc='best')
    plt.savefig(f'{city}_{district_eng}/{city}_{district_eng}_MAE.png')
    
    # test
    model = keras.models.load_model(f'{city}_{district_eng}/{city}_{district_eng}_model-1.h5')
    y_test = np.array(test_data[test_data.columns[-1]]).reshape(len(test_data),1)
    test_data = (test_data - mean) / std
    x_test = np.array(test_data[test_data.columns[0:feature_count]])
    y_t = np.array(test_data[test_data.columns[-1]])
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
    result = pd.concat([y_test, y_pred],axis=1)
    result.to_csv(f'{city}_{district_eng}/{city}_{dist}_result.csv')
    
if __name__ == '__main__':
    code = input("欲處理的城市簡稱: ")
    dist = input("欲處理的鄉鎮市區: ")
    dist_eng = input("欲處理的鄉鎮市區英文簡稱: ")
    train(code,dist, dist_eng)