import json
from pathlib import Path

import click
import pandas as pd
import yaml
import logging

from .utils import map_value, flatten_nest_dict


def get_all_configs_and_results(root_dir: Path):
    all_runs = []
    for p in root_dir.glob("**"):
        if (p / "checkpoints" / "res.json").exists():
            with open(p / "checkpoints" / "res.json") as f:
                this_run = {f"result/{key}": value for key, value in json.load(f).items()}
            with open(p / "config.json") as f:
                this_run.update(json.load(f))
            this_run = flatten_nest_dict(this_run)
            all_runs.append(this_run)
    df = pd.DataFrame.from_records(all_runs)
    for col in df.columns:
        if "dir" in col or not pd.api.types.is_hashable(df[col][0]) or len(df[col].unique()) == 1:  # type: ignore
            df.drop(col, inplace=True, axis=1)
    return df


def map(df: pd.DataFrame, map_file: Path):
    with open(map_file) as f:
        maps = yaml.load(f, Loader=yaml.SafeLoader)
    df.drop(columns=maps["redundancy"], inplace=True)
    for column, map in maps["map"].items():
        df[column] = df[column].map(lambda x: map_value(x, map))
    return df


def get_mean_std(df: pd.DataFrame) -> pd.DataFrame:
    if "runtime/seed" not in df.columns:
        logging.warning("No Different Seeds, std is not calculated")
    else:
        df.drop(columns=["runtime/seed"], inplace=True)

    para_list = [c for c in df.columns if not c.startswith("result") and c != "runtime/seed"]
    res = pd.concat(
        [
            df.groupby(para_list).mean().rename(lambda x: x + "_mean", axis=1),
            df.groupby(para_list).std().rename(lambda x: x + "_std", axis=1),
        ],
        axis=1,
    )
    return res.reset_index()


@click.command()
@click.option("--seed/--no-seed", help="whether to save the mean/std after merging across seeds", default=True)
@click.option("--raw/--no-raw", help="whether to save the raw results without merging across seeds", default=True)
@click.option("--xlsx/--no-xlsx", help="whether to save the results in xlsx format", default=True)
@click.option(
    "-m",
    "--mapping",
    help="the path to the file containing the mapping rules",
    type=click.Path(exists=True, path_type=Path),
    default=Path(__file__).parents[1] / "maps/default.yml",
)
@click.argument("path", type=click.Path(exists=True, path_type=Path))
def gather_results(seed, raw, path, mapping, xlsx):
    all_results = get_all_configs_and_results(path)
    all_results = map(all_results, mapping)
    if raw:
        all_results.to_csv(path / "raw_results.csv", index=False)
        if xlsx:
            all_results.to_excel(path / "raw_results.xlsx", index=False)
    if seed:
        merge_results = get_mean_std(all_results)
        merge_results.to_csv(path / "results.csv", index=False)
        if xlsx:
            merge_results.to_excel(path / "results.xlsx", index=False)
    return


if __name__ == "__main__":
    gather_results()
