"""CLI entry point: click group, interactive menu, settings, update."""
import os
import subprocess
import sys
from shutil import which
from unittest import result

import click

from eagleosint.config import CONFIGS, logger, save_config
from eagleosint.display import (
    RED, YELLOW, BLUE, WHITE, DARK_GRAY, LIGHT_RED,
    BG_WHITE, BG_RED,
    SPACE_PREFIX, LOGO,
)
from eagleosint.providers.bitly import bypass_bitly
from eagleosint.providers.facebook import Facebook
from eagleosint.providers.github import github_lookup
from eagleosint.providers.godorker import godorker
from eagleosint.providers.mailfinder import mailfinder
from eagleosint.providers.network import infoga, iplocation
from eagleosint.providers.phoneinfo import phoneinfo
from eagleosint.providers.tempmail import temp_mail_gen
from eagleosint.providers.userrecon import userrecon


def menu():
    """Displays the main menu of the E4GL30S1NT toolkit."""
    os.system("clear")
    print(LOGO)
    print(
        f"""
         {BG_WHITE}\\033[2;30m Choose number or type exit for exiting {WHITE}

        {WHITE}{BLUE}  01{WHITE} Userrecon     {DARK_GRAY} Username reconnaissance
        {WHITE}{BLUE}  02{WHITE} Facedumper    {DARK_GRAY} Dump facebook information
        {WHITE}{BLUE}  03{WHITE} Mailfinder    {DARK_GRAY} Find email with name
        {WHITE}{BLUE}  04{WHITE} Godorker      {DARK_GRAY} Dorking with google search
        {WHITE}{BLUE}  05{WHITE} Phoneinfo     {DARK_GRAY} Phone number information
        {WHITE}{BLUE}  06{WHITE} DNSLookup     {DARK_GRAY} Domain name system lookup
        {WHITE}{BLUE}  07{WHITE} Whoislookup   {DARK_GRAY} Identify who is on domain
        {WHITE}{BLUE}  08{WHITE} Sublookup     {DARK_GRAY} Subnetwork lookup
        {WHITE}{BLUE}  09{WHITE} Hostfinder    {DARK_GRAY} Find host domain
        {WHITE}{BLUE}  10{WHITE} DNSfinder     {DARK_GRAY} Find host domain name system
        {WHITE}{BLUE}  11{WHITE} RIPlookup     {DARK_GRAY} Reverse IP lookup
        {WHITE}{BLUE}  12{WHITE} IPlocation    {DARK_GRAY} IP to location tracker
        {WHITE}{BLUE}  13{WHITE} Bitly Bypass  {DARK_GRAY} Bypass all bitly urls
        {WHITE}{BLUE}  14{WHITE} Github Lookup {DARK_GRAY} Dump GitHub information
        {WHITE}{BLUE}  15{WHITE} TempMail {DARK_GRAY}      Generate Temp Mail and Mail Box
        {WHITE}{BLUE}  00{WHITE} Exit          {DARK_GRAY} bye bye ):
        """
    )


def mainmenu():
    """Handles the main menu input and navigation."""
    fb_instance = None
    while True:
        menu()
        try:
            cmd = input(f"{SPACE_PREFIX}{WHITE}{BLUE}>{WHITE} choose:{BLUE} ")
            if int(len(cmd)) < 6:
                logger.info("command dispatched: %s", cmd.strip())
                if cmd in ("exit", "Exit", "00", "0"):
                    sys.exit(RED + SPACE_PREFIX + "* Exiting !" + WHITE)
                elif cmd in ("1", "01"):
                    userrecon()
                elif cmd in ("2", "02"):
                    if fb_instance is None:
                        fb_instance = Facebook()
                    fb_instance.facedumper()
                elif cmd in ("3", "03"):
                    mailfinder()
                elif cmd in ("4", "04"):
                    godorker()
                elif cmd in ("5", "05"):
                    phoneinfo()
                elif cmd in ("6", "06"):
                    infoga("dnslookup")
                elif cmd in ("7", "07"):
                    infoga("whois")
                elif cmd in ("8", "08"):
                    infoga("subnetcalc")
                elif cmd in ("9", "09"):
                    infoga("hostsearch")
                elif cmd in ("10"):
                    infoga("mtr")
                elif cmd in ("11"):
                    infoga("reverseiplookup")
                elif cmd in ("12"):
                    iplocation()
                elif cmd in ("13"):
                    bypass_bitly()
                elif cmd in ("14"):
                    github_lookup()
                elif cmd in ("15"):
                    temp_mail_gen()
            else:
                continue
        except KeyboardInterrupt:
            sys.exit(f"{RED}\n{SPACE_PREFIX}* Aborted !")


def settings():
    """Allows the user to change settings in the config file."""
    os.system("clear")
    print(LOGO)
    print(f"         {WHITE}{BG_RED} \\033[1mSETTINGS CHANGER MODE {WHITE}\n")

    setting_counter = 0
    config_options = {}
    for setting_key_name, setting_value_item in CONFIGS.items():
        if setting_key_name != "headers":
            setting_counter += 1
            config_options[str(setting_counter)] = setting_key_name
            print(
                f"         {WHITE}{RED}  0{setting_counter} {setting_key_name}"
                + " " * (20 - len(setting_key_name))
                + f'{LIGHT_RED}:  "{setting_value_item}" '
            )
    exit_option_key = "exit".upper()
    print(
        f"         {WHITE}{RED}  00{RED} {exit_option_key}"
        + " " * (20 - len(exit_option_key))
        + f"{LIGHT_RED}:  bye bye ): "
    )

    chosen_option = ""
    while chosen_option not in config_options:
        chosen_option = input(
            f"{SPACE_PREFIX}{LIGHT_RED}>{RED} What do you want to change?{LIGHT_RED} "
        )
        if chosen_option in ("0", "00"):
            sys.exit()

    new_setting_value = input(
        f"{SPACE_PREFIX}{LIGHT_RED}>{RED} Insert the new value of "
        f"{config_options[chosen_option]} :{LIGHT_RED} "
    )
    CONFIGS[config_options[chosen_option]] = new_setting_value
    save_config()


def _run_update() -> None:
    if which("termux-setup-storage"):
        script_path = "$PREFIX/bin/E4GL30S1NT"
    elif os.path.isdir("/usr/local/bin"):
        script_path = "/usr/local/bin/E4GL30S1NT"
    else:
        script_path = "/usr/bin/E4GL30S1NT"
    update_url = "https://raw.githubusercontent.com/C0MPL3XDEV/E4GL3OS1NT/main/E4GL30S1NT.py"
    try:
        print(f"{YELLOW}Updating script at {script_path}...{WHITE}")
        subprocess.run(["wget", update_url, "-O", script_path], check=True, timeout=60)
        subprocess.run(["chmod", "+x", script_path], check=True, timeout=10)
        print(f"{BLUE}>{WHITE} Script updated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"{RED}Update failed: {e}{WHITE}")
    except FileNotFoundError:
        print(f"{RED}wget or chmod command not found. Install them and retry.{WHITE}")
    except subprocess.TimeoutExpired:
        print(f"{RED}Update timed out. Check your internet connection and retry.{WHITE}")


def _write_output(
    results: list,
    fmt: str,
    filepath: str | None,
) -> None:
    """Write structured output to file or stdout."""
    from eagleosint.output import write_results
    if filepath:
        with open(filepath, "w", encoding="utf-8") as fh:
            write_results(results, fmt, fh)
        print(f"{BLUE}>{WHITE} output written to {filepath}")
    else:
        write_results(results, fmt)

@click.group(
    invoke_without_command=True,
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.pass_context
def main(ctx: click.Context) -> None:
    """E4GL30S1NT — Simple Information Gathering Toolkit.

    Run without arguments to enter the interactive menu.
    """
    if ctx.invoked_subcommand is None:
        mainmenu()


@main.command("userrecon")
def cmd_userrecon() -> None:
    """Username reconnaissance across 71 platforms."""
    print(LOGO)
    userrecon()


@main.command("facedumper")
def cmd_facedumper() -> None:
    """Dump Facebook friend list information."""
    print(LOGO)
    fb = Facebook()
    fb.facedumper()


@main.command("mailfinder")
def cmd_mailfinder() -> None:
    """Find email addresses from a name."""
    print(LOGO)
    mailfinder()


@main.command("godorker")
def cmd_godorker() -> None:
    """Google dorking with result scraping."""
    print(LOGO)
    godorker()


@main.command("phoneinfo")
def cmd_phoneinfo() -> None:
    """Phone number information and validation."""
    print(LOGO)
    phoneinfo()


@main.command("dns")
def cmd_dns() -> None:
    """DNS lookup for a domain or IP."""
    print(LOGO)
    infoga("dnslookup")


@main.command("whois")
def cmd_whois() -> None:
    """WHOIS lookup for a domain."""
    print(LOGO)
    infoga("whois")


@main.command("subnet")
def cmd_subnet() -> None:
    """Subnet / network calculator."""
    print(LOGO)
    infoga("subnetcalc")


@main.command("hostfinder")
def cmd_hostfinder() -> None:
    """Find hosts for a domain."""
    print(LOGO)
    infoga("hostsearch")


@main.command("dnsfinder")
def cmd_dnsfinder() -> None:
    """DNS finder via MTR."""
    print(LOGO)
    infoga("mtr")


@main.command("riplookup")
def cmd_riplookup() -> None:
    """Reverse IP lookup."""
    print(LOGO)
    infoga("reverseiplookup")


@main.command("iplocation")
@click.option("--output", "-o", type=click.Choice(["json", "csv"]), default=None,
              help="Emit structured output.")
@click.option("--output-file", "-f", "output_file", type=click.Path(), default=None,
              help="Write output to this file path.")
def cmd_iplocation(output: str | None, output_file: str | None) -> None:
    """IP address geolocation."""
    print(LOGO)
    result = iplocation()
    if output and result:
        _write_output([result], output, output_file)


@main.command("bitly")
@click.option("--output", "-o", type=click.Choice(["json", "csv"]), default=None,
              help="Emit structured output.")
@click.option("--output-file", "-f", "output_file", type=click.Path(), default=None,
              help="Write output to this file path.")
def cmd_bitly(output: str | None, output_file: str | None) -> None:
    """Resolve and bypass Bitly short URLs."""
    print(LOGO)
    result = bypass_bitly()
    if output and result:
        _write_output([result], output, output_file)


@main.command("github")
@click.option("--output", "-o", type=click.Choice(["json", "csv"]), default=None,
              help="Emit structured output instead of (or in addition to) terminal display.")
@click.option("--output-file", "-f", "output_file", type=click.Path(), default=None,
              help="Write output to this file path.")
def cmd_github(output: str | None, output_file: str | None) -> None:
    """GitHub user profile lookup."""
    print(LOGO)
    result = github_lookup()
    if output and result:
        _write_output(result, output, output_file)

@main.command("tempmail")
def cmd_tempmail() -> None:
    """Generate a temporary email and monitor inbox."""
    print(LOGO)
    temp_mail_gen()


@main.command("update")
def cmd_update() -> None:
    """Update E4GL30S1NT to the latest version."""
    _run_update()


@main.command("settings")
def cmd_settings() -> None:
    """Edit API keys and configuration."""
    settings()