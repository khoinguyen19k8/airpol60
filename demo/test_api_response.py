"""
Read from city_coords all city names then attempt to get the newest air pollution information for each of them.
"""
from configparser import ConfigParser
from argparse import ArgumentParser, FileType
import pandas as pd
import requests
import time
import logging
import json


def set_up():
    """
    Set up run time params, config and logger.
    """
    parser = ArgumentParser()
    parser.add_argument("--config_file", type=FileType("r"))
    parser.add_argument("--seeds", type=str, help="seed directory path")
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()

    config = ConfigParser()
    config.read_file(args.config_file)

    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel("INFO")
    return args, config, logger


def get_city_air_pollution(lat, lon, city, api_key, logger):
    """
    Pass in latitude, longitude, and api_key as per OpenWeather API
    to get the latest air pollution information.
    """
    endpoint = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    try:
        res = requests.get(endpoint, timeout=3)
        if res.status_code != 200:
            logger.error("Unable to request weather data")
            logger.error(res.text)
            return {"Error": res.text, "StatusCode": res.status_code}
    except requests.exceptions.Timeout:
        logger.error("Request timed out")
        return {"Error": "Request timed out"}

    conformed_res = {}
    conformed_res["city"] = city
    conformed_res["lon"] = res.json()["coord"]["lon"]
    conformed_res["lat"] = res.json()["coord"]["lat"]
    conformed_res["air_quality_index"] = res.json()["list"][0]["main"]["aqi"]
    aq_comps = res.json()["list"][0]["components"]
    for component in aq_comps:
        conformed_res[component] = aq_comps[component]
    conformed_res["observed_date"] = res.json()["list"][0]["dt"]
    conformed_res["ingested_date"] = int(time.time())
    return conformed_res


def main():
    args, config, logger = set_up()
    API_KEY = config["OPENWEATHER"]["API_KEY"]
    city_df = pd.read_csv(f"{args.seeds}/city_coords.csv")
    cities = list(city_df["city"])
    for city in cities:
        logger.info(f"Start producing air pollution data for {city}")
        lat, lon = (
            city_df.loc[city_df["city"] == city]["lat"].iloc[0],
            city_df.loc[city_df["city"] == city]["lon"].iloc[0],
        )
        conformed_res = get_city_air_pollution(lat, lon, city, API_KEY, logger)
        encoded_res = json.dumps(conformed_res)

        if args.test is True:
            print(conformed_res)
            with open(f"json_dumps/{city}_{int(time.time())}.json", "w") as f:
                f.write(encoded_res)


if __name__ == "__main__":
    main()
