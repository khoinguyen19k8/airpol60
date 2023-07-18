import os
import requests
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
import pandas as pd


def main():
    parser = ArgumentParser()
    parser.add_argument("--config_file", type=FileType("r"))
    args = parser.parse_args()

    config = ConfigParser()
    config.read_file(args.config_file)
    city_coords = pd.read_csv("../seeds/city_coords.csv")
    pass


if __name__ == "__main__":
    pass
