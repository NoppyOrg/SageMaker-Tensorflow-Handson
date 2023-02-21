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

# Endpointの削除
predictor2.delete_endpoint()
