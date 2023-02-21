# SageMaker-Tensorflow-Hans-on
## ハンズオン構成
![architecture](architecture.svg)

- 概要
    - 手元のPC(mac/linuxを想定)にてPythonスクリプトを使用して、MNISTデータセットの分類モデルをトレーニングし、その後に推論を実行します。
    - コンテナは、SageMaker提供のコンテナを利用します。
    - 最初に`src/training_and_save.py`を実行し、トレーニングとトレーニング済みモデルを利用し推論エンドポイントを準備します。
    - その後`src/invoke_inference.py`を利用し作成した推論用エンドポイントを利用し推論を実行します。

- 元のsampleからの違い
    - ベースは、[amazon-sagemaker-examples](https://github.com/aws/amazon-sagemaker-examples/)の[ensorflow_script_mode_training_and_serving](https://github.com/aws/amazon-sagemaker-examples/blob/main/sagemaker-python-sdk/tensorflow_script_mode_training_and_serving/tensorflow_script_mode_training_and_serving.ipynb)(日本語は[こちら](https://github.com/aws-samples/aws-ml-jp/blob/main/sagemaker/tensorflow2-training-and-serving/tensorflow2_training_and_serving.ipynb))です
    - 元はSageMakerのnotebookやSageMaker Labでの実行を前提としていますが、本ハンズオンは手元のPCでnotebookを使用せず実行する前提のハンズオンにしています。
    - 元のsampleからの変更点は以下になります
        - SageMaker実行ロール: 元は作業環境のロールをそのまま利用する前提のコードですが、本ハンズオンは作業用のロールとSageMakerの実行ロールを分ける前提で実装しています。
        - 学習と推論のスクリプト分離: 学習と推論を別々に実行する前提で、スクリプトを分けました。

## Step1: 事前準備
### 実行環境の確認
作業環境に以下のソフトウェアがセットアップされていることを確認します。ない場合はインストールします。
- python3
- pip3(sagemakerのセットアップ用)
- AWS CLI(事前の動作確認用)

SageMakerを実行したい環境用のプロファイルがあることを確認します。ここではプロファイル名に`sagemaker-poc-profile`という名前を利用していると仮定します。
以下の例のようにUserIdやアカウントIDが取得できれば問題ありません。
なおこの実行ロールには、`AdministratorAccess`相当の権限が付与されている前提とします(SageMaker用の実行ロール作成のため)。
```sh
#プロファイル名は環境に合わせた名前を指定する
PROFILE="sagemaker-poc-profile"
export PROFILE
echo "PROFILE=${PROFILE}"
```
```sh
aws --profile ${PROFILE} sts get-caller-identity
{
    "UserId": "AROAQH6XODSXUFCH7NNDU:botocore-session-1676905613",
    "Account": "999999999999",
    "Arn": "arn:aws:sts::999999999999:assumed-role/OrganizationAccountAccessRole/botocore-session-1676905613"
}
```
### SageMaker用の実行ロールとS3バケットの作成
```sh
aws --profile ${PROFILE} cloudformation deploy \
    --stack-name SageMakerPoC \
    --template-file "./CFn/execute_role.yaml" \
    --capabilities CAPABILITY_IAM ;
```


### python仮想環境の準備
今回は手元のPCで実行するため、PC環境にSageMaker SDKが残らないように、ハンズオン用のpython仮想環境を準備します。これはハンズオン固有の設定になるため、SageMakerの利用上は必要はありません。
- 仮想環境の作成
```sh
python3 -m venv sagemaker-hans-on
```
- 仮想環境のアクティブ化
```sh
source sagemaker-hans-on/bin/activate
```
### 必要なPythonライブラリのセットアップ
```sh
pip3 install sagemaker matplotlib
```
### 事前作成したIAMロールとS3バケット情報の設定
トレーニング&推論実行時に引き渡すために、SageMakerの実行ロールとデフォルトS3バケットの情報を環境変数に設定します。
```sh
#ClientのPrivate IP取得
ExecuteRoleArn=$(aws --profile ${PROFILE} --output text \
    cloudformation describe-stacks \
        --stack-name SageMakerPoC \
        --query 'Stacks[].Outputs[?OutputKey==`RoleArn`].[OutputValue]')
BucketName=$(aws --profile ${PROFILE} --output text \
    cloudformation describe-stacks \
        --stack-name SageMakerPoC \
        --query 'Stacks[].Outputs[?OutputKey==`BucketName`].[OutputValue]')
export ExecuteRoleArn BucketName
#設定確認
env | grep -e ExecuteRoleArn -e BucketName
```
### (オプション)トレーニングデータの確認
デモ用のトレーニングデータとして、SageMakerがデモ用にS3にてPublicで提供しているMNISTデータベースを利用します。

```sh
#東京リージョンの対象バケットのパス(東京リージョンの場合)
aws s3 ls s3://sagemaker-sample-data-ap-northeast-1/tensorflow/mnist/
2019-01-25 08:31:41   31360128 eval_data.npy
2019-01-25 08:31:41      40128 eval_labels.npy
2019-01-25 08:31:41  172480128 train_data.npy
2019-01-25 08:31:41     220128 train_labels.npy
```
## Step2: トレーニングの実行と推論エンドポイントの作成
### トレーニングの実行/モデル保存/推論エンドポイント作成
```sh
python3 src/training_and_save.py
```
### 結果の確認と環境変数の設定
- トレーニング済みデータ
```sh
JOB_NAME="<training_and_save.py実行最後に出力されたJob Name>"
export JOB_NAME
aws --profile ${PROFILE} s3 ls "s3://${BucketName}/${JOB_NAME}/output/"
```
- エンドポイントの確認
```sh
ENDPOINT_NAME="<training_and_save.py実行最後に出力されたEndpoint Name"
export ENDPOINT_NAME
aws --profile ${PROFILE} sagemaker describe-endpoint --endpoint-name ${ENDPOINT_NAME}
```

## Step3: 推論の実行
### 推論用のデータをローカルに取得
```sh
mkdir inference
cd inference
```
```sh
aws --profile ${PROFILE} s3 \
    cp s3://sagemaker-sample-data-ap-northeast-1/tensorflow/mnist/eval_data.npy eval_data.npy
aws --profile ${PROFILE} s3 \
    cp s3://sagemaker-sample-data-ap-northeast-1/tensorflow/mnist/eval_labels.npy eval_labels.npy
```
### 実行
```sh
python3 ../src/invoke_inference.py
```

## Step4: クリーンナップ
### 推論エンドポイントの削除
```sh
python3 ../src/remove_inference_endpoint.py
```
### ローカルデータの削除
```sh
cd ..
rm -rf inference
```
### python仮想環境の終了
```sh
deactivate
```