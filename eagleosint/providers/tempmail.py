"""Temporary email generation and inbox polling via 1secmail API."""
import json
import os
import random
import re
import sys
from getpass import getpass
from time import sleep

import requests
from tabulate import tabulate

from eagleosint.display import (
    RED, BLUE, WHITE,
    SPACE_PREFIX,
)
from eagleosint.session import session as _session

TEMPMAIL_API_URL     = "https://www.1secmail.com/api/v1/"
TEMPMAIL_MAILBOX_URL = "https://www.1secmail.com/mailbox"
ALL_MAILS_DIRNAME    = "All Mails"

MAIL_PRINTATE: list = []


def temp_mail_gen():
    """Generates a temporary email address and checks for incoming mail."""
    temp_api_url = TEMPMAIL_API_URL
    domain_choices = ["1secmail.com", "1secmail.net", "1secmail.org"]
    chosen_domain = random.choice(domain_choices)

    _new_mail_url_local = ""

    def extract_mail_details_nested(mail_url_to_extract):
        username_match = re.search(r"login=(.*)&", mail_url_to_extract)
        domain_match   = re.search(r"domain=(.*)", mail_url_to_extract)
        if username_match and domain_match:
            return [username_match.group(1), domain_match.group(1)]
        return [None, None]

    def delete_temp_mail_nested(current_mail_address, mail_url_for_delete):
        delete_url = TEMPMAIL_MAILBOX_URL
        extracted_details = extract_mail_details_nested(mail_url_for_delete)
        if extracted_details[0] and extracted_details[1]:
            delete_data = {
                "action": "deleteMailbox",
                "login": extracted_details[0],
                "domain": extracted_details[1],
            }
            print(f"Disposing your email address - {current_mail_address}\n")
            try:
                _session.post(delete_url, data=delete_data, timeout=10)
            except requests.exceptions.RequestException as e_delete:
                print(f"{RED}Error deleting email: {e_delete}{WHITE}")

    def check_temp_mails_nested(mail_url_to_check):
        extracted_details = extract_mail_details_nested(mail_url_to_check)
        if not (extracted_details[0] and extracted_details[1]):
            return

        check_link = (
            f"{temp_api_url}?action=getMessages"
            f"&login={extracted_details[0]}&domain={extracted_details[1]}"
        )
        try:
            response_data = _session.get(check_link, timeout=10).json()
            if len(response_data) != 0:
                mail_ids = [
                    item.get("id") for item in response_data if item.get("id")
                ]
                mails_dir = os.path.join(os.getcwd(), ALL_MAILS_DIRNAME)
                os.makedirs(mails_dir, exist_ok=True)

                for mail_item_id in mail_ids:
                    if mail_item_id not in MAIL_PRINTATE:
                        MAIL_PRINTATE.append(mail_item_id)
                        read_msg_link = (
                            f"{temp_api_url}?action=readMessage"
                            f"&login={extracted_details[0]}"
                            f"&domain={extracted_details[1]}&id={mail_item_id}"
                        )
                        msg = _session.get(read_msg_link, timeout=10).json()
                        mail_table_data = [
                            ["From",    msg.get("from", "")],
                            ["Subject", msg.get("subject", "")],
                            ["Content", msg.get("textBody", "")],
                            ["Date",    msg.get("date", "")],
                        ]
                        for line_item_text in tabulate(
                            mail_table_data,
                            headers=["info", "content"],
                            tablefmt="fancy_grid",
                        ).splitlines():
                            print(f"{SPACE_PREFIX}   {WHITE}{line_item_text}")
                        print()
        except requests.exceptions.RequestException as e_check:
            print(f"{RED}Error checking emails: {e_check}{WHITE}")
        except json.JSONDecodeError:
            print(f"{RED}Error decoding email list.{WHITE}")

    current_mail_address_local = ""
    try:
        custom_email_name = input(
            f"{SPACE_PREFIX}{BLUE}>{WHITE} Insert a custom name for the email:{BLUE} "
        )
        _new_mail_url_local = (
            f"{temp_api_url}?login={custom_email_name}&domain={chosen_domain}"
        )
        try:
            _session.get(_new_mail_url_local, timeout=10)
        except requests.exceptions.RequestException as e_register:
            print(f"{RED}Error registering temporary email: {e_register}{WHITE}")
            return

        extracted = extract_mail_details_nested(_new_mail_url_local)
        if extracted[0] and extracted[1]:
            current_mail_address_local = f"{extracted[0]}@{extracted[1]}"
            print(
                f"{SPACE_PREFIX}{BLUE}>{WHITE} Temp mail: "
                f"{BLUE}{current_mail_address_local}"
            )
            getpass(f"{SPACE_PREFIX}{BLUE}> {WHITE}Press enter to continue")
            print(
                f"{SPACE_PREFIX}{BLUE}-------------------[ INBOX ]-------------------\n"
            )
            while True:
                check_temp_mails_nested(_new_mail_url_local)
                sleep(5)
        else:
            print(f"{RED}Could not create temporary email address.{WHITE}")

    except KeyboardInterrupt:
        if current_mail_address_local and _new_mail_url_local:
            delete_temp_mail_nested(current_mail_address_local, _new_mail_url_local)
        sys.exit(f"{RED}\n{SPACE_PREFIX}* Aborted Temp Mail!{WHITE}")
    except requests.exceptions.RequestException as e_temp_mail_req:
        print(f"{RED}A network error occurred in Temp Mail: {e_temp_mail_req}{WHITE}")
        if current_mail_address_local and _new_mail_url_local:
            delete_temp_mail_nested(current_mail_address_local, _new_mail_url_local)
        sys.exit()
    except Exception as e_temp_mail_other:
        print(f"{RED}An unexpected error occurred in Temp Mail: {e_temp_mail_other}{WHITE}")
        if current_mail_address_local and _new_mail_url_local:
            delete_temp_mail_nested(current_mail_address_local, _new_mail_url_local)
        sys.exit()