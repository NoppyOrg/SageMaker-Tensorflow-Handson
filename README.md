# SageMaker-Tensorflow-Hans-on




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
### ハンズオン仮想環境のセットアップ
- sagemaker SDKのセットアップ
```sh
pip3 install sagemaker
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
## Step2: トレーニングの実行とトレーニング済みモデルの保存保存
### トレーニングの実行とモデル保存
```sh
python3 src/training_and_save.py
```
### トレーニング結果データの確認
```sh
JOB_NAME="<training_and_save.py実行最後に出力されたJob Name>"
export JOB_NAME
aws --profile ${PROFILE} s3 ls "s3://${BucketName}/${JOB_NAME}/"
```
### トレーニング済みモデル格納先S3のuriの環境変数設定
次の推論の準備として、トレーニング済みモデルの格納先のs3を環境変数に設定します。
```sh
MODEL_S3_URI="s3://${BucketName}/${JOB_NAME}/output/model.tar.gz"
export MODEL_S3_URI

#データの確認
aws --profile ${PROFILE} s3 ls ${MODEL_S3_URI}
```
## Step3: 推論の実行
### 推論用のデータをローカルに取得
```sh
mkdir inference
cd inference
```
```sh
aws --profile ${PROFILE} s3 \
    cp s3://sagemaker-sample-data-ap-northeast-1/tensorflow/mnist/train_data.npy train_data.npy
aws --profile ${PROFILE} s3 \
    cp s3://sagemaker-sample-data-ap-northeast-1/tensorflow/mnist/train_labels.npy train_labels.npy
```
### 実行
```sh
python3 ../src/deploy_model_and_invoke.py
```