from logging import getLogger, StreamHandler, DEBUG, INFO
import sys
import os
import boto3  # Sagemaker SDKとしては必須ではないが、任意のAWSプロファイルを指定して実行するため利用。
import sagemaker
from sagemaker import tensorflow
import matplotlib.pyplot as plt
import numpy as np

# ログ出力設定
stdout_handler = StreamHandler(stream=sys.stdout)
stdout_handler.setLevel(DEBUG)
logger = getLogger(__name__)
logger.setLevel(DEBUG)
logger.addHandler(stdout_handler)

# 環境変数の取得
endpoint_name = os.environ.get("ENDPOINT_NAME")

# セッション作成
boto3_session = boto3.Session(profile_name="sagemaker-poc-profile")
sagemaker_session = sagemaker.Session(boto_session=boto3_session)

# デバック情報出力
logger.debug("endpoint_name      = {}".format(endpoint_name))


# Sagemakerの推論用エンドポイントの設定
predictor2 = tensorflow.model.TensorFlowPredictor(
    endpoint_name, sagemaker_session=sagemaker_session)


# 推論用の入力データの準備
print("loading data for inference.\n")
eval_data = np.load('eval_data.npy').reshape(-1, 28, 28, 1)
eval_labels = np.load('eval_labels.npy')


# 推論の実行
print("execute inference.\n")
k = 1000  # choose your favorite number from 0 to 9950
test_data = eval_data[k:k+50]
test_data

for i in range(5):
    for j in range(10):
        plt.subplot(5, 10, 10 * i + j+1)
        plt.imshow(test_data[10 * i + j, :].reshape(28, 28), cmap='gray')
        plt.title(10 * i + j+1)
        plt.tick_params(labelbottom=False, labelleft=False)
        plt.subplots_adjust(wspace=0.2, hspace=1)
plt.show()

predictions = predictor2.predict(test_data.reshape(-1, 28, 28, 1))
for i in range(0, 50):
    prediction = np.argmax(predictions['predictions'][i])
    label = eval_labels[i+k]
    print(' [{}]: prediction is {}, label is {}, matched: {}'.format(
        i+1, prediction, label, prediction == label))
