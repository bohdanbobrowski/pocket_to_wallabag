#!/usr/bin/env python3
from datetime import datetime

import requests
import webbrowser
import sys
import logging


file_handler = logging.FileHandler(filename="pocket_to_wallabag.log")
stdout_handler = logging.StreamHandler(stream=sys.stdout)
handlers = [file_handler, stdout_handler]
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    handlers=handlers,
)
logger = logging.getLogger(__name__)


from pocket_to_wallabag.settings import ImporterSettings

COUNT = 30
JSON_HEADERS = {"X-Accept": "application/json"}


def err_on_status_code(result, msg):
    if result.status_code != 200:
        logger.error(f"{msg} : {result.status_code} - {result.text}")
        sys.exit(1)


def get_pocket_request_token() -> str:
    payload = {
        "consumer_key": ImporterSettings().pocket_consumer_key,
        "redirect_uri": ImporterSettings().redirect_uri,
    }
    response = requests.post(
        f"{ImporterSettings().pocket_url}/oauth/request",
        data=payload,
        headers=JSON_HEADERS,
    )
    err_on_status_code(response, "[pocket] error while getting request token")
    pocket_request_token = response.json()["code"]
    logger.info(f"[pocket] request_token = {pocket_request_token}")
    return pocket_request_token


def get_pocket_access_token(pocket_request_token) -> str:
    webbrowser.open(
        f"https://getpocket.com/auth/authorize?request_token={pocket_request_token}&redirect_uri={ImporterSettings().redirect_uri}",
        new=2,
    )
    print(
        f"if your browser did not open, please go to : https://getpocket.com/auth/authorize?request_token={pocket_request_token}&redirect_uri={ImporterSettings().redirect_uri}"
    )
    input("If you have authorized the app, please press Enter to continue...")
    payload = {
        "consumer_key": ImporterSettings().pocket_consumer_key,
        "code": pocket_request_token,
    }
    response = requests.post(
        f"{ImporterSettings().pocket_url}/oauth/authorize",
        data=payload,
        headers=JSON_HEADERS,
    )
    err_on_status_code(response, "[pocket] error while getting access token")
    pocket_access_token = response.json()["access_token"]
    logger.info(f"[pocket] access_token = {pocket_access_token}")
    return pocket_access_token


def get_wallabag_access_token(settings: ImporterSettings) -> str:
    payload = {
        "grant_type": "password",
        "client_id": settings.wallabag_client_id,
        "client_secret": settings.wallabag_client_secret,
        "username": settings.wallabag_username,
        "password": settings.wallabag_password,
    }
    response = requests.post(
        f"{ImporterSettings().wallabag_url}/oauth/v2/token",
        data=payload,
        headers=JSON_HEADERS,
    )
    err_on_status_code(response, "[wallabag] error while getting access token")
    wallabag_access_token = response.json()["access_token"]
    logger.info(f"[wallabag] access_token = {wallabag_access_token}")
    return wallabag_access_token


def get_pocket_urls(
    settings: ImporterSettings, pocket_access_token, offset: int = 0
) -> (list[str], bool):
    """Docs: https://getpocket.com/developer/docs/v3/retrieve"""
    continue_download = True
    payload = {
        "consumer_key": settings.pocket_consumer_key,
        "access_token": pocket_access_token,
        "sort": "oldest",
        "detailType": "simple",
        "count": f"{COUNT}",
        "offset": f"{offset}",
    }
    result = requests.post(
        f"{settings.pocket_url}/get", data=payload, headers=JSON_HEADERS
    )
    err_on_status_code(result, "[pocket] error while getting items")
    all_items = result.json()["list"]
    logger.info(f"[pocket] got {len(all_items)} items")
    if len(all_items) < COUNT:
        logger.info("[pocket] this is the last part of articles")
        continue_download = False
    return all_items, continue_download


def send_to_wallabag(settings: ImporterSettings, wallabag_access_token, urls):
    """Docs: https://doc.wallabag.org/developer/api/methods/"""
    headers = {
        "X-Accept": "application/json",
        "Authorization": f"Bearer {wallabag_access_token}",
    }
    for pocket_id, url in urls.items():
        if int(url["status"]) < 2:
            tags = list(url["tags"].keys())
            tags.append("pocket")
            archive = 0
            if int(url["status"]) > 0 or int(url["time_read"]) > 0:
                archive = 1
            payload = {
                "url": url["resolved_url"] or url["given_url"],
                "title": url["resolved_title"] or url["given_title"],
                "tags": ",".join(tags),
                "archive": archive,
                "starred": int(url["favorite"]),
                "language": url["lang"],
                "published_at": url["time_added"],
            }
            response = requests.post(
                f"{settings.wallabag_url}/api/entries.json",
                data=payload,
                headers=headers,
            )
            if response.status_code != 200:
                logger.error(
                    f"[wallabag] error while importing {url["given_url"]} : {response.status_code} - {response.text}"
                )
            else:
                logger.info(f"[wallabag] success importing {url["given_url"]}")


def main():
    importer_settings = ImporterSettings()
    pocket_request_token = get_pocket_request_token()
    pocket_access_token = get_pocket_access_token(pocket_request_token)
    continue_download = True
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = open(f"pocket_articles_{timestamp}.csv", "w")
    csv_file.write(
        '"#","pocket_id","given_url","resolved_url","given_title","resolved_title","status","time_added","time_read","favorite","lang","tags"\n'
    )
    cnt = 0
    offset = 0
    while continue_download:
        urls_from_pocket, continue_download = get_pocket_urls(
            importer_settings, pocket_access_token, offset
        )
        for pocket_id, url in urls_from_pocket.items():
            if int(url["status"]) < 2:
                cnt += 1
                tags = list(url["tags"].keys())
                csv_file.write(
                    f'"{cnt}.","{pocket_id}","{url["given_url"]}","{url["resolved_url"]}","{url["given_title"]}",'
                    + f'"{url["resolved_title"]}","{url["status"]}","{url["time_added"]}","{url["time_read"]}",'
                    + f'"{url["favorite"]}","{url["lang"]}","{",".join(tags)}"'
                    + "\n"
                )
        wallabag_access_token = get_wallabag_access_token(importer_settings)
        send_to_wallabag(importer_settings, wallabag_access_token, urls_from_pocket)
        offset += COUNT
    csv_file.close()


if __name__ == "__main__":
    main()
