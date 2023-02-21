from logging import getLogger, StreamHandler, DEBUG, INFO
import sys
import os
import boto3  # Sagemaker SDKとしては必須ではないが、任意のAWSプロファイルを指定して実行するため利用。
import sagemaker
from sagemaker import get_execution_role
from sagemaker.tensorflow import TensorFlow
import numpy as np

# ログ出力設定
stdout_handler = StreamHandler(stream=sys.stdout)
stdout_handler.setLevel(DEBUG)
logger = getLogger(__name__)
logger.setLevel(DEBUG)
logger.addHandler(stdout_handler)

# 環境変数の取得
execute_role = os.environ.get("ExecuteRoleArn")
default_bucket = os.environ.get("BucketName")
model_dir_s3 = os.environ.get("MODEL_S3_URI")

# セッション作成
boto3_session = boto3.Session(profile_name="sagemaker-poc-profile")
sagemaker_session = sagemaker.Session(
    boto_session=boto3_session, default_bucket=default_bucket)

# IAMロール/実行リージョン/デフォルトバケット取得
region = sagemaker_session.boto_session.region_name

# デバック情報出力
logger.debug("model_dir_s3      = {}".format(model_dir_s3))
logger.debug("region            = {}".format(region))
logger.debug("execute_role      = {}".format(execute_role))
logger.debug("default_bucket    = {}".format(
    sagemaker_session.default_bucket()))

# 推論用の入力データの準備
train_data = np.load("train_data.npy")
train_labels = np.load("train_labels.npy")

# Sagemakerの推論用のEstimator
# https://sagemaker.readthedocs.io/en/stable/frameworks/tensorflow/sagemaker.tensorflow.html
mnist_estimator2 = TensorFlow(
    entry_point=None,
    model_dir=model_dir_s3,
    role=execute_role,
    instance_count=2,
    framework_version="2.1.0",
    py_version="py3",
    distribution={"parameter_server": {"enabled": True}},
    sagemaker_session=sagemaker_session,
)
