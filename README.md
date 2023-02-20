# SageMaker-Tensorflow-Hans-on




## 手順
### 実行環境の確認
作業環境に以下のソフトウェアがセットアップされていることを確認します。ない場合はインストールします。
- python3
- pip3(sagemakerのセットアップ用)
- AWS CLI(事前の動作確認用)

SageMakerを実行したい環境用のプロファイルがあることを確認します。ここではプロファイル名に`sagemaker-poc-profile`という名前を利用していると仮定します。
以下の例のようにUserIdやアカウントIDが取得できれば問題ありません。
```sh
aws --profile sagemaker-poc-profile sts get-caller-identity
{
    "UserId": "AROAQH6XODSXUFCH7NNDU:botocore-session-1676905613",
    "Account": "999999999999",
    "Arn": "arn:aws:sts::999999999999:assumed-role/OrganizationAccountAccessRole/botocore-session-1676905613"
}
```
### python仮想環境の準備
ハンズオン用のpython仮想環境を準備します
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











### トレーニングデータ
トレーニングデータは、


### トレーニングの実行
```sh
python3 src/training_and_save.py
```