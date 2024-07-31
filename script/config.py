from pathlib import Path
import datetime

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class AnalyticsConfig(BaseModel):
    date_range: tuple[datetime.date, datetime.date] = (datetime.datetime(2024, 4, 1).date(), datetime.datetime(2024, 8, 31).date())

class DataPath(BaseModel):
    query_template: Path = Path('./query_template.txt')
    target_users: Path = Path('./target_users.csv')

    output_dir: Path = Path('../outputs')
    pr_csv: Path = output_dir / 'prs.csv'
    comment_csv: Path = output_dir / 'comments.csv'
    pr_counts_csv: Path = output_dir / 'pr_counts_by_user.csv'
    pr_counts_png: Path = output_dir / 'pr_counts_by_user.png'
    comment_counts_csv: Path = output_dir / 'comment_counts_by_user.csv'
    comment_counts_png: Path = output_dir / 'comment_counts_by_user.png'


class EnvConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    GITHUB_TOKEN: str
    ORGANIZATION: str
    ENDPOINT_GRAPHQL: str
