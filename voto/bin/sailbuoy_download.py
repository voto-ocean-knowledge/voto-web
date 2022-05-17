import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json
import logging
import os
import sys
from pathlib import Path

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, folder)
_log = logging.getLogger(__name__)
with open(f"{folder}/mongo_secrets.json") as json_file:
    secrets = json.load(json_file)
data_dir = Path("/data/sailbuoy/raw")


def download_sailbuoy(sb_id):
    _log.info("start sailbuoy download process")
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(
        executable_path="/usr/bin/chromedriver", options=chrome_options
    )
    _log.info("configured driver")
    driver.get("https://ids.sailbuoy.no")  # load webpage
    driver.find_element("id", "UserName").send_keys(secrets["sb_user"])
    driver.find_element("id", "Password").send_keys(secrets["sb_password"])
    element = driver.find_element(
        "css selector", "input[type='submit']"
    )  # find the submit button
    element.click()  # click the submit button
    time.sleep(2)  # give the page time to load
    _log.info("logged in ")
    # make the cookies accessible for the session
    session = requests.Session()
    cookies = driver.get_cookies()
    for cookie in cookies:
        session.cookies.set(cookie["name"], cookie["value"])

    _log.info("start downloads")
    download_link1 = f"https://ids.sailbuoy.no/GenCustomData/_DownloadAllAsCSV?instrName={sb_id}D"  # Payload
    download_link2 = f"https://ids.sailbuoy.no/GenCustomData/_DownloadAllAsCSV?instrName={sb_id}A"  # Autopilot
    response1 = session.get(download_link1)
    response2 = session.get(download_link2)
    # at this point, the downloadable csv files are stored in the response object
    _log.info("write data to file")
    if not data_dir.exists():
        data_dir.mkdir(parents=True)
    with open(data_dir / f"{sb_id}_nav.csv", "w") as file:
        file.write(str(response1.text))
        _log.info(f"wrote {sb_id}_nav.csv")
    with open(data_dir / f"{sb_id}_pld.csv", "w") as file:
        file.write(str(response2.text))
        _log.info(f"wrote {sb_id}_pld.csv")


if __name__ == "__main__":
    logging.basicConfig(
        filename=f"{secrets['log_dir']}/voto_add_sailbuoy.log",
        filemode="a",
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    download_sailbuoy("SB2016")
    download_sailbuoy("SB2120")
    _log.info("Finished download of sailbuoy data\n")
