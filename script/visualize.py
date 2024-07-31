import datetime
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from config import DataPath, AnalyticsConfig

def aggregate(datapath: Path, output_path: Path, target_column: str, date_column: str, date_range: tuple[datetime.date, datetime.date], target_users: list[str]) -> pd.DataFrame:
    df = pd.read_csv(datapath, dtype=str)
    df[date_column] = pd.to_datetime(df[date_column]).dt.date
    df = df[(df[date_column] >= date_range[0]) & (df[date_column] <= date_range[1])]
    df = df[df[target_column].isin(target_users)]

    # ユーザごとのPR数を集計
    counts = df[target_column].value_counts().reset_index()
    counts.columns = [target_column, 'counts']

    # 件数0のユーザを集計結果に追加
    other_users =[]
    aggregated_users = counts[target_column].to_list()
    for user in target_users:
        if not user in aggregated_users:
            other_users.append((user, 0))
    zeros = pd.DataFrame.from_records(other_users, columns=[target_column, 'counts'])

    summary = pd.concat([counts, zeros], axis=0)
    summary = summary.reset_index(drop=True)

    # 集計結果をCSVとして保存
    summary.to_csv(output_path, index=False)

    return summary

def plot(counts: pd.DataFrame, x_column: str, y_column: str, output_path: Path, horizontal: bool = False, title: str = 'counts') -> None:
    fig, ax = plt.subplots(figsize=(20, 10))

    # グラフを描画
    plt.figure(figsize=(10, 6))

    plt.title(title, fontsize=12)

    ax.tick_params(direction='in')
    plt.gca().spines["right"].set_visible(False)
    plt.gca().spines["left"].set_visible(False)
    plt.gca().spines["top"].set_visible(False)

    if horizontal:
        ax.set_xlabel(y_column, fontsize=14)
        ax.set_ylabel(x_column, fontsize=14)

        plt.grid(axis="x")
        plt.barh(counts[x_column], counts[y_column], color='skyblue')
    else:
        ax.set_xlabel(x_column, fontsize=14)
        ax.set_ylabel(y_column, fontsize=14)

        plt.xticks(rotation=70)
        plt.grid(axis="y")
        plt.bar(counts[x_column], counts[y_column], color='skyblue')

    plt.tight_layout()

    # グラフをPNGとして保存
    plt.savefig(output_path)

    # グラフを表示
    #plt.show()

def main():
    analytics_config = AnalyticsConfig()
    datapath = DataPath()

    date_range = analytics_config.date_range
    target_users = pd.read_csv(datapath.target_users)["user_name"].to_list()

    pr_counts = aggregate(
        datapath=datapath.pr_csv,
        output_path=datapath.pr_counts_csv,
        target_column='pr_author',
        date_column='pr_created_at',
        date_range=date_range,
        target_users=target_users
    )
    plot(
        counts=pr_counts,
        x_column='pr_author',
        y_column='counts',
        output_path=datapath.pr_counts_png,
        title=f"The number of PRs by user between {date_range[0].strftime('%Y/%m/%d')} and {date_range[1].strftime('%Y/%m/%d')}",
    )

    comments_counts = aggregate(
        datapath=datapath.comment_csv,
        output_path=datapath.comment_counts_csv,
        target_column='comment_author',
        date_column='pr_created_at',
        date_range=date_range,
        target_users=target_users
    )
    plot(
        counts=comments_counts,
        x_column='comment_author',
        y_column='counts',
        output_path=datapath.comment_counts_png,
        title=f"The number of comments by user between {date_range[0].strftime('%Y/%m/%d')} and {date_range[1].strftime('%Y/%m/%d')}",
        horizontal=True
    )

if __name__ == "__main__":
    main()
