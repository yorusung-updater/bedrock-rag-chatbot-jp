# Amazon BedrockでマルチモーダルRAGチャットボットを簡単に構築する実践ガイド

#### 目次
- Step 1. [Knowledge base と連携する S3 ソースバケットの作成](#step-1-s3-source-bucket)
- Step 2. [Bedrock knowledge base の作成](#step-2-create-kb)
  - （任意）[検索性能を高めるために Chunking and parsing configurations を設定](#optional-chunking-parsing)
- Step 3. [EC2 にチャットボットアプリケーションをデプロイ](#step-3-deploy-ec2)
- Step 4. [デプロイしたアプリケーションのテスト](#step-4-test-app)

- - - 

生成AIの重要性が高まる中、従来のモデル学習から始まるMLOpsよりも低コストで、目的の文書内容に基づいたAIの結果を生成できるRAG（Retrieval-Augmented Generation、検索拡張生成）が注目されています。RAGは、カスタムデータを活用し、大規模言語モデルが回答を生成する前に学習データソース外のカスタム知識ベースを参照させるプロセスを指します。RAGを用いた生成AIは、大規模データベースから関連情報を検索しそれを基に回答を生成するため、モデルを再学習させることなく特定ドメインや組織の内部知識に基づいてLLM機能を拡張できる、費用対効果の高いアプローチです。

![image](https://github.com/user-attachments/assets/08d4a781-7a30-4fb3-ac34-d1a4203898d4)

Amazon BedrockもRAG構築を容易にするKnowledge base機能を提供しています。Amazon Bedrock Knowledge baseを使うと、数回のクリックでFMをOpenSearchなどのRAG用データソースに接続してテストできます。本記事ではAmazon Bedrock Knowledge baseを使って高性能RAGを簡単に構築する方法を説明し、そのRAGを下図のようなチャットボットアプリケーションとしてEC2にデプロイする方法をコードとともに段階的に紹介します。

## Architecture & Demo
![image](https://github.com/user-attachments/assets/3211645d-c4c5-4507-ac6e-19b19cb3d495)

![image](https://github.com/user-attachments/assets/e67285aa-77a9-46e7-ad48-9e283b398eef)

<a id="step-1-s3-source-bucket"></a>
## Step 1. Knowledge base と連携する S3 ソースバケットの作成

まず、Bedrock Knowledge base と連携する S3 バケットを作成する必要があります。該当リンクをクリックして ap-northeast-1（オレゴン）リージョンで AWS S3 Console にアクセスし、新しいバケットを作成できます。後続の手順で Bedrock Knowledge base を作成する際にこのバケット名を使うため、一意で覚えやすい名前を入力し、他の設定は既定値のままバケットを作成します。

![image](https://github.com/user-attachments/assets/da5820a9-c84c-4a7d-a736-cbf361d1dc32)

バケット作成が完了したら、RAGで検索したい文書をそのバケットに事前にアップロードします。
（本ハンズオンでは50ページ分のEC2ユーザーガイドPDFをアップロードしました: [ec2_userguide_1-50.pdf](./sampledata/ec2_userguide_1-50.pdf) ）


<a id="step-2-create-kb"></a>
## Step 2. Bedrock knowledge base の作成

### Bedrock モデルアクセスの申請
Bedrock Console にアクセスし、まず Bedrock サービスで使用するファウンデーションモデル（FM）へのアクセスを申請する必要があります。下のスクリーンショットのように左サイドバーで Model access をクリックして申請ページに移動します。

![image](https://github.com/user-attachments/assets/58b97443-b281-48af-8b33-f01f84ff7cf1)

以下のように Model access ページで「Enable specific models」をクリックします。

![image](https://github.com/user-attachments/assets/0c54aa49-15da-4301-839e-57c85a854d0d)

本ハンズオンで使用するモデルは以下です。該当モデルを選択して Next（次へ）をクリックします。

* Claude 3 Sonnet
* Titan Embeddings G1 - Text
* Titan Text Embeddings V2

![image](https://github.com/user-attachments/assets/acbd9184-4b09-4bf3-9d75-b74927f6b902)

Access 申請を希望するモデルが正しく選択されていることを確認し、Submit（送信）をクリックして申請を完了します。一部のモデルは Access 付与まで時間がかかる場合があります。申請が完了すると、以下のように Access Status が Access granted に変更されます。

![image](https://github.com/user-attachments/assets/bdce9377-b828-4d3b-8f69-98d7afdddb9d)

### Bedrock knowledge base の作成と S3 データソースの接続

これで Bedrock Knowledge base を作成する準備ができました。Bedrock Console の左サイドバーで Knowledge bases（ナレッジベース）をクリックし、作成画面に移動して「Create knowledge base」ボタンをクリックします。

![image](https://github.com/user-attachments/assets/e5a89406-9361-41d9-b483-5c6cb0fc7e49)

以下のように設定し、「Next（次へ）」ボタンを押して次の設定へ進みます。

![image](https://github.com/user-attachments/assets/c17dc933-8d6d-403e-86e1-8ebcf4f8bda4)

次は Knowledge base の Data source を設定する段階です。「Browse S3」ボタンをクリックし、先ほど [Step 1] で作成したバケットを選択します。

![image](https://github.com/user-attachments/assets/b45ce095-8c94-43f7-a278-9c36420ba31a)
![image](https://github.com/user-attachments/assets/15725123-3d54-4fdf-8ef0-cc449c661968)

<a id="optional-chunking-parsing"></a>
### （任意）検索性能を高めるために Chunking and parsing configurations を設定

RAGの検索性能を高めたい場合（特に画像や表が含まれる複雑な文書で情報を検索したい場合）は、このセクションを検討してください。RAGシステムを複雑な実アプリケーションに適用するためには、画像や表のデータも適切に検索できるマルチモーダル処理能力が必要です。2024.07.10 に Bedrock に新しく追加された「Chunking and parsing configurations」設定を通じて、これらの性能を改善しマルチモーダルRAGを実装できます。

LLMを活用したパーシング機能は、PDFのような非構造化文書の情報を構造化し、画像やテーブルに含まれる情報も検索可能な形でインデックス化するのに役立ちます。以下のように「Chunking and parsing configurations」を「Custom」に選択し、Parsing strategy で「Use foundation model for parsing」チェックボックスを選択した後、パーシングに使うモデルを「Claude 3 Sonnet v1」と「Claude 3 Haiku v1」のいずれかから選びます。（本ハンズオンでは Sonnet v1 モデルを使用します）

![image](https://github.com/user-attachments/assets/47a603ed-e8f6-44b0-88d4-1c9ed7491585)

上のスクリーンショットで赤い四角で示した部分が、パーシングのために LLM に渡すプロンプトです。このプロンプトは自由に修正できますが、本ハンズオンでは既定のプロンプトをそのまま使用しました。既定プロンプトの内容を要約すると以下の通りです。

```
1. 各ページを注意深く確認し、ヘッダー、本文テキスト、脚注、表、画像、ページ番号などページ内のすべての要素を特定してMarkdown形式に変換します。
    * メインタイトルには #、セクションには ##、下位セクションには ### などを使用（その他ガイドは省略）
2. Visualization（画像など）要素を見つけた場合は、その詳細な説明を作成します。
3. Table（表）要素を見つけた場合は、Markdownテーブルに変換します。
```

このように LLM パーシング機能は、文書を検索可能な形で埋め込む前に、上記のようなプロンプトで LLM が構造を再定義することで、テキストはもちろん画像や表に対する検索性能も高められます。LLM を使用するため、大容量文書で利用する際はコストを考慮することをおすすめします。

その後 Chunking strategy も設定できます。既定の Default chunking 以外を選べますが、前述の LLM パーシングにより文書を Markdown 形式でパースしたため、本ガイドでは Hierachical chunking を選択しました。Token size もユースケースに適したサイズに合わせて設定し、「Next（次へ）」を押して次の段階へ進みます。

![image](https://github.com/user-attachments/assets/532db6e6-2002-4f2d-94b6-9d174bf19e1c)

当該 LLM parsing 機能を利用した結果、以下のように複雑な表/画像の図も高い性能で retrieve できることを確認できます。

<img width="565" alt="image" src="https://github.com/user-attachments/assets/a03b5353-2970-4b91-8bb2-aa4d16b10f09">

> さまざまな Chunking 戦略やメタデータ処理設定については、次のブログ記事を参照すると良いでしょう。対象文書のサイズ、種類、その他の特性を考慮し、状況に合った Chunking オプションを選ぶことが RAG の性能向上に役立ちます: https://aws.amazon.com/ko/blogs/machine-learning/amazon-bedrock-knowledge-bases-now-supports-advanced-parsing-chunking-and-query-reformulation-giving-greater-control-of-accuracy-in-rag-based-applications/

### 埋め込みモデルの選択とベクターDBとしての OpenSearch Serverless の作成
使用する Embedding モデルを選択できます。本ハンズオンでは Titan text Embeddings v2 モデルを選択します。Vector dimensions も RAG の精度と速度に影響するため、既定値以外に任意で設定可能です。
Vector database としては「Quick create a new vector store」オプションを選択して OpenSearch Serverless を新規作成します。その後「Next（次へ）」ボタンを押して確認段階へ移動し、確認後「Create knowledge base」ボタンをクリックして Knowledge base を作成します。設定どおりに Knowledge base を構成し OpenSearch Serverless を作成するには数分かかります。

![image](https://github.com/user-attachments/assets/fa4f8f51-9f2e-4d30-8ee4-7aec1000ab8c)
![image](https://github.com/user-attachments/assets/4fa02e60-279f-40e2-a076-5ea65515ef75)

### 作成した Knowledge Base をコンソールでテスト
Knowledge base が正常に作成されました。Data source に先ほど [Step 1] で作成した S3 バケットが接続されていることを確認できます。該当 Data source を選択し、「Sync」ボタンをクリックしてバケット内のデータを Knowledge base に連携します。データサイズにより数分から数時間かかる場合があります。

![image](https://github.com/user-attachments/assets/0a243c29-39ad-4e82-a49b-07b706473e6e)
![image](https://github.com/user-attachments/assets/fec762b2-a629-4803-89aa-f328aa9649a3)
![image](https://github.com/user-attachments/assets/1af4bda3-2faf-4632-ba30-0592011b2d90)

<a id="step-3-deploy-ec2"></a>
## Step 3. EC2 にチャットボットアプリケーションをデプロイ

### EC2 の作成
* 「Ubuntu」サーバーで作成します。（本ハンズオンでは Ubuntu Server 24.04 LTS、SSD Volume Type を使用します。）
* セキュリティグループに SSH（22 ポート）と HTTP（80）に対する inbound rule を追加します。
* 本ハンズオンではインスタンスタイプ m5.large を使用します。

![image](https://github.com/user-attachments/assets/dead46f2-f6de-4b2e-b0c7-4d337ef082e0)
![image](https://github.com/user-attachments/assets/d932d83a-fec3-4efd-9933-009713ed02f2)

### ソースコードのダウンロードと必要パッケージのインストール
EC2 が作成されたら、EC2 にアクセスし root ディレクトリで以下のコマンドを入力します。
```
sudo apt update 
sudo apt-get install -y ec2-instance-connect
sudo apt-get install -y git
sudo apt-get install -y python3-pip
sudo apt-get install -y python3.12-venv

git clone https://github.com/ottlseo/bedrock-rag-chatbot.git && git checkout ec2-manual-deployment

sudo python3 -m venv --copies /home/ubuntu/my_env
sudo chown -R ubuntu:ubuntu /home/ubuntu/my_env
source /home/ubuntu/my_env/bin/activate

cd bedrock-rag-chatbot/application

pip3 install -r requirements.txt
```

### 作成した Bedrock Knowledge base ID をソースコード内の variables.py に入力

- [Step 2] で作成した Bedrock KB コンソールから ID をコピーした後、
  - ![image](https://github.com/user-attachments/assets/d473a37b-8af0-4382-9c3e-eb1191e7b680)
- Clone したコードの variables.py ファイルを開き、KNOWLEDGE_BASE_ID 変数にコピーした ID を割り当てます。
  - ![image](https://github.com/user-attachments/assets/525a7b8b-f77a-48f0-a7fb-1fe2fb95345d)

### EC2 へのデプロイ
EC2 で以下のコマンドを入力してエディタを開きます。
```
sudo vi /etc/systemd/system/streamlit.service
```
その後開いたエディタに以下の内容を貼り付けます。
```
[Unit]
Description=Streamlit App
After=network.target

[Service]
User=ubuntu
Environment='AWS_DEFAULT_REGION=us-west-2'
WorkingDirectory=/home/ubuntu/bedrock-rag-chatbot/application
ExecStartPre=/bin/bash -c 'sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8501'
ExecStart=/bin/bash -c 'source /home/ubuntu/my_env/bin/activate && streamlit run streamlit.py --server.port 8501'
Restart=always

[Install]
WantedBy=multi-user.target
```

入力後は `:wq` を入力してエディタを終了し、以下のコマンドで Streamlit アプリケーションを起動します。
```
sudo systemctl daemon-reload
sudo systemctl enable streamlit
sudo systemctl start streamlit

```

→ これで EC2 のパブリック IP から Streamlit アプリケーションにアクセスできます。

- - -

<a id="step-4-test-app"></a>
# Step 4. デプロイしたアプリケーションのテスト

#### サンプル質問: 
- `EC2とは何ですか？`
  - 期待回答: Amazon Elastic Compute Cloud (Amazon EC2) は Amazon Web Services (AWS) クラウドで提供されるオンデマンドでスケーラブルなコンピューティング容量サービスです。Amazon EC2 を使うとハードウェアコストを削減し、アプリケーションをより迅速に開発・デプロイできます。必要な数の仮想サーバーを起動し、セキュリティとネットワーキングを構成し、ストレージを管理できます。EC2 インスタンスは AWS クラウドで実行される仮想サーバーです。EC2 インスタンスを起動すると、選択したインスタンスタイプに応じて割り当てられるハードウェアリソースが決まります。各インスタンスタイプは CPU、メモリ、ネットワーク、ストレージ、およびグラフィックスの各リソースのさまざまな組み合わせを提供します。
- `Amazon Bedrockとは何ですか？`
  - 期待回答: 提供された検索結果には「Amazon Bedrock」に関する情報がないため、正確な回答ができません。
- `PowerShell 向けの AWS tool について説明してください。`
  - 期待回答: AWS は PowerShell 向けの AWS Tools for Windows PowerShell モジュールを提供しています。このモジュールは AWS SDK for .NET の機能を基盤としており、PowerShell コマンドラインから AWS リソースに対する操作をスクリプト化できます。AWS Tools for Windows PowerShell を使うと Amazon EC2 などの AWS サービス向けの cmdlet を利用できます。AWS Tools for Windows PowerShell を始めるには AWS Tools for Windows PowerShell ユーザーガイドを参照してください。Amazon EC2 の cmdlet は AWS Tools for PowerShell Cmdlet Reference で確認できます。
