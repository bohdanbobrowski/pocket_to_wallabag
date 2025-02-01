#!/usr/bin/env python3

import requests
import webbrowser
import sys

from pocket_to_wallabag.settings import ImporterSettings


def err_on_status_code(request, msg):
    if request.status_code != 200:
        print(f"{msg} : {request.status_code} - {request.text}")
        sys.exit(1)


def main():
    # REQUESTS CONFIG
    headers = {"X-Accept": "application/json"}

    # 1 + 2 - send request to get request token
    payload = {
        "consumer_key": ImporterSettings().pocket_consumer_key,
        "redirect_uri": ImporterSettings().redirect_uri,
    }
    r = requests.post(
        f"{ImporterSettings().pocket_url}/oauth/request", data=payload, headers=headers
    )

    err_on_status_code(r, "[pocket] error while getting request token")

    POCKET_REQUEST_TOKEN = r.json()["code"]
    print(f"[pocket] request_token = {POCKET_REQUEST_TOKEN}")

    # 3 - redirect user
    webbrowser.open(
        f"https://getpocket.com/auth/authorize?request_token={POCKET_REQUEST_TOKEN}&redirect_uri={ImporterSettings().redirect_uri}",
        new=2,
    )
    print(
        f"if your browser did not open, please go to : https://getpocket.com/auth/authorize?request_token={POCKET_REQUEST_TOKEN}&redirect_uri={ImporterSettings().redirect_uri}"
    )

    # TODO replace this input with a socket that will listen to the callback of the oAuth, so we dont have to use a user interaction
    input("If you have authorized the app, please press Enter to continue...")

    # 4 - get access token
    payload = {
        "consumer_key": ImporterSettings().pocket_consumer_key,
        "code": ImporterSettings().pocket_request_token,
    }
    r = requests.post(
        f"{ImporterSettings().pocket_url}/oauth/authorize",
        data=payload,
        headers=headers,
    )

    err_on_status_code(r, "[pocket] error while getting access token")

    POCKET_ACCESS_TOKEN = r.json()["access_token"]
    print(f"[pocket] access_token = {POCKET_ACCESS_TOKEN}")

    # 5 - get items
    payload = {
        "consumer_key": ImporterSettings().pocket_consumer_key,
        "access_token": POCKET_ACCESS_TOKEN,
        "state": "unread",
        "sort": "oldest",
        "detailType": "simple",
    }
    r = requests.post(
        f"{ImporterSettings().pocket_url}/get", data=payload, headers=headers
    )

    err_on_status_code(r, "[pocket] error while getting items")

    # 6 - create list of urls
    all_items = r.json()["list"]
    urls = [item["given_url"] for item in all_items.values()]

    # 7 - wallabag oAuth - get access token
    payload = {
        "grant_type": "password",
        "client_id": ImporterSettings().wallabag_client_id,
        "client_secret": ImporterSettings().wallabag_client_secret,
        "username": ImporterSettings().wallabag_username,
        "password": ImporterSettings().wallabag_password,
    }
    r = requests.post(
        f"{ImporterSettings().wallabag_url}/oauth/v2/token",
        data=payload,
        headers=headers,
    )

    err_on_status_code(r, "[wallabag] error while getting access token")

    WALLABAG_ACCESS_TOKEN = r.json()["access_token"]
    print(f"[wallabag] access_token = {WALLABAG_ACCESS_TOKEN}")
    headers = {
        "X-Accept": "application/json",
        "Authorization": f"Bearer {WALLABAG_ACCESS_TOKEN}",
    }
    for index, url in enumerate(urls):
        payload = {
            "url": url,
            "tags": "pocket",
        }
        r = requests.post(
            f"{ImporterSettings().wallabag_url}/api/entries.json",
            data=payload,
            headers=headers,
        )

        if r.status_code != 200:
            print(
                f"[wallabag] error while importing {index+1}/{len(urls)} {url} : {r.status_code} - {r.text}"
            )
        else:
            print(f"[wallabag] success importing {index+1}/{len(urls)} : {url}")

    print("done :) gg! your pocket items were successfully migrated to wallabag")


if __name__ == "__main__":
    main()
