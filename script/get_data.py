import requests
import csv
import tqdm
from pathlib import Path

from config import DataPath, EnvConfig

def load_query_template(filepath: Path) -> str:
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def fetch_data(query_template: str, organization: str, headers: dict[str, str], url: str, cursor: None | str = None) -> dict:
    cursor_part = f'"{cursor}"' if cursor else 'null'
    query = query_template.format(
        organization=organization,
        cursor_part=cursor_part
    )
    response = requests.post(url, json={'query': query}, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed to run by returning code of {response.status_code}. {query}")

def save_to_csv(data: list[str], headers: list[str], filepath: Path) -> None:
    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for row in data:
            writer.writerow(row)

def main():
    # 環境変数の設定
    datapath = DataPath()
    env_config = EnvConfig()

    # GitHubのアクセストークン
    headers = {"Authorization": f"Bearer {env_config.GITHUB_TOKEN}"}

    # Organization名
    organization = env_config.ORGANIZATION

    # GraphQLエンドポイント
    url = env_config.ENDPOINT_GRAPHQL

    # GraphQLクエリのテンプレート
    query_template = load_query_template(datapath.query_template)

    cursor = None
    has_next_page = True
    pr_data = []
    comment_data = []

    pr_id = 0
    comment_id = 0

    with tqdm.tqdm() as pbar:
        while has_next_page:
            result = fetch_data(
                query_template=query_template,
                organization=organization,
                headers=headers,
                url=url,
                cursor=cursor,
            )
            org_data = result['data']['organization']
            repositories = org_data['repositories']['edges']

            # 各リポジトリの情報を処理
            for repo in repositories:
                repo_name = repo['node']['name']
                pull_requests = repo['node']['pullRequests']['edges']

                for pr in pull_requests:
                    pr_node = pr['node']
                    pr_created_at = pr_node['createdAt']
                    pr_author = pr_node['author']['login']

                    # PRの詳細情報をリストに追加
                    pr_data.append([pr_id, pr_created_at, repo_name, pr_author])

                    comments = pr_node['comments']['edges']
                    for comment in comments:
                        comment_node = comment['node']
                        comment_author = comment_node['author']['login']
                        comment_body = comment_node['body']

                        # コメントの詳細情報をリストに追加
                        comment_data.append([pr_id, pr_created_at, repo_name, comment_id, comment_author, comment_body])
                        comment_id += 1
                        pbar.update(1)
                    pr_id += 1

            # ページネーション情報を更新
            page_info = org_data['repositories']['pageInfo']
            cursor = page_info['endCursor']
            has_next_page = page_info['hasNextPage']

    datapath.output_dir.mkdir(parents=True)
    # PRの詳細情報をCSVに保存
    pr_headers = ['pr_id', 'pr_created_at', 'repository_name', 'pr_author']
    save_to_csv(pr_data, pr_headers, datapath.pr_csv)

    # コメントの詳細情報をCSVに保存
    comment_headers = ['pr_id', 'pr_created_at', 'repository_name', 'comment_id', 'comment_author', 'comment_body']
    save_to_csv(comment_data, comment_headers, datapath.comment_csv)

if __name__ == "__main__":
    main()
