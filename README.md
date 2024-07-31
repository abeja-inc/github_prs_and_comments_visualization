# ディレクトリの説明
- `script`
  - `config.py`: ファイルのパスや環境変数の設定, 集計期間の指定
  - `get_data.py`: GraphQL を使って Organization に紐づくリポジトリからデータを取得
  - `visualize.py`: ユーザ毎のPR数およびコメント数を集計し、結果を可視化
  - `query_template.txt`: Githubからデータを取得する際のクエリのテンプレート
  - `target_users.csv`: 集計対象のユーザを指定
- `output`: 集計結果のcsvデータとその可視化画像を格納する

# 使用方法
0. 環境構築
  - `poetry install`
1. `script` 配下に下記の形式の `.env` を作成
  - 内容
      ```
      GITHUB_TOKEN=""
      ORGANIZATION="abeja-inc"
      ENDPOINT_GRAPHQL="https://api.github.com/graphql"
      ```
  - `GITHUB_TOKEN` はアカウントの setting から発行できる Personal Access Token
2. 集計期間の指定
  - `config.py` の `AnalyticsConfig` の　`date_range` のデフォルト値を変更する
    - Sample) `date_range: tuple[datetime.date, datetime.date] = (datetime.datetime(2024, 4, 1).date(), datetime.datetime(2024, 8, 31).date())`
3. 集計対象のユーザを指定
  - カラム名を `user_name` として、集計対象のユーザ一覧を csv データとして作成する
4. `script` に移動して `get_data.py` を実行し、 GitHub からデータを取得
5. 同じく `script` 下で `visualize.py` を実行し、データの集計および可視化を実行
6. `outputs` 下に集計結果とその可視化画像が格納されるので確認
