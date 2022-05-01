#! /usr/bin/env python3
# Authors: C0MPL3XDEV & JProgrammer-it
# Support me with follow my instagram page and github page 
# Disclaimer: please dont edit or recode the original source code !
# Last update: 21/09/2021 - version 1.1

import os
import sys
import re
import json
import requests
import textwrap
import socket
from lxml.html import fromstring
from getpass import getpass
from shutil import which
from threading import Thread
from time import sleep
from bs4 import BeautifulSoup
from tabulate import tabulate
import pyperclip
import requests
import random
import string
import time
import sys
import re
import os


r = "\033[31m"
g = "\033[32m"
y = "\033[33m"
b = "\033[34m"
p = "\033[35m"
d = "\033[2;37m"
w = "\033[0m"
lr = "\u001b[38;5;196m"

W = f"{w}\033[1;47m"
R = f"{w}\033[1;41m"
G = f"{w}\033[1;42m"
Y = f"{w}\033[1;43m"
B = f"{w}\033[1;44m"


mail_printate = []
configs = json.loads(open("configs/config.json", "r").read())
home = os.getenv("HOME")
cookifile = f"{home}/.cookies"
space = "         "
lines =  space + "-"*44
apihack = "https://api.hackertarget.com/{}/?q={}"
mbasic = "https://mbasic.facebook.com{}"
graph = "https://graph.facebook.com{}"
userrecon_num = 0
userrecon_working = 0
userrecon_results = []
check_email_num = 0
headers = {"User-Agent":"Opera/9.80 (J2ME/MIDP; Opera Mini/9.80 (S60; SymbOS; Opera Mobi/23.334; U; id) Presto/2.5.25 Version/10.54"}
logo = f"""{b}
      .---.        .-----------
     /     \  __  /    ------
    / /     \(  )/    -----           
   //////   ' \/ `   ---            ┏───────────────────────────────┓
  //// / // :    : ---              │     WELCOME TO E4GL30S1NT     │
 // /   /  /`    '--                │     https://c0mpl3xdev.tk     │
//          //..\\                  │ https://JProgrammerIt.web.app │
       ====UU====UU====             └───────────────────────────────┘
           '//||\\`
             ''``
  {d}Simple Information Gathering Toolkit{w}    
  {d}Authors: {w}{r}@C0MPL3XDEV{d} & {w}{r}@JProgrammer-it{w}
"""

def menu():
    os.system("clear")
    print(logo)
    print(f"""
         {W}\033[2;30m Choose number or type exit for exiting {w}
    
        {w}{b}  01{w} Userrecon     {d} Username reconnaissance 
        {w}{b}  02{w} Facedumper    {d} Dump facebook information
        {w}{b}  03{w} Mailfinder    {d} Find email with name
        {w}{b}  04{w} Godorker      {d} Dorking with google search
        {w}{b}  05{w} Phoneinfo     {d} Phone number information
        {w}{b}  06{w} DNSLookup     {d} Domain name system lookup
        {w}{b}  07{w} Whoislookup   {d} Identify who is on domain
        {w}{b}  08{w} Sublookup     {d} Subnetwork lookup
        {w}{b}  09{w} Hostfinder    {d} Find host domain
        {w}{b}  10{w} DNSfinder     {d} Find host domain name system
        {w}{b}  11{w} RIPlookup     {d} Reverse IP lookup
        {w}{b}  12{w} IPlocation    {d} IP to location tracker
        {w}{b}  13{w} Bitly Bypass  {d} Bypass all bitly urls
        {w}{b}  14{w} Github Lookup {d} Dump GitHub information
        {w}{b}  15{w} TempMail {d}      Generate Temp Mail and Mail Box
        {w}{b}  00{w} Exit          {d} bye bye ):
        """)
    mainmenu()

def mainmenu():
    while True: 
        try:
            cmd = input(f"{space}{w}{b}>{w} choose:{b} ")
            if int(len(cmd)) < 6:
                if cmd in ("exit","Exit", "00", "0"): exit(r+space+"* Exiting !"+w)
                elif cmd in ("1","01"): userrecon()
                elif cmd in ("2","02"): fb.facedumper()
                elif cmd in ("3","03"): mailfinder()
                elif cmd in ("4","04"): godorker()
                elif cmd in ("5","05"): phoneinfo()
                elif cmd in ("6","06"): infoga("dnslookup")
                elif cmd in ("7","07"): infoga("whois")
                elif cmd in ("8","08"): infoga("subnetcalc")
                elif cmd in ("9","09"): infoga("hostsearch")
                elif cmd in ("10"): infoga("mtr")
                elif cmd in ("11"): infoga("reverseiplookup")
                elif cmd in ("12"): iplocation()
                elif cmd in ("14"): github_lookup()
                elif cmd in ("13"): bypass_bitly()
                elif cmd in ("15"): temp_mail_gen()
            else: continue
        except KeyboardInterrupt:
            exit(f"{r}\n{space}* Aborted !")

def display_progress(iteration, total, text=""):
    bar_max_width = 40  # chars
    bar_current_width = bar_max_width * iteration // total
    bar = "█" * bar_current_width + " " * (bar_max_width - bar_current_width)
    progress = "%.1f" % (iteration / total * 100)
    print(f"{space}{iteration}/{total} |{bar}| {progress}% {text}", end="\r")
    if iteration == total:
        print()

def send_req(url, username):
    try:
        req = requests.get(url.format(username), headers=headers)
    except requests.exceptions.Timeout: pass
    except requests.exceptions.TooManyRedirects: pass
    except requests.exceptions.ConnectionError: pass
    global userrecon_num, userrecon_results, userrecon_working
    userrecon_num += 1
    

    if req.status_code == 200: color = g; userrecon_working += 1
    elif req.status_code == 404: color = r
    else: color = y

    percent = 71/100*userrecon_num
    display_progress(userrecon_num, 71, f"FOUND: {userrecon_working}")

    userrecon_results.append(f"  {space}{b}[{color}{req.status_code}{b}] {userrecon_num}/71 {w}{url.format(username)}")

def check_email(email, api, total, ok, f):

    response = requests.get("https://isitarealemail.com/api/email/validate",params = {'email': email}, headers = {'Authorization': "Bearer " + api })
    status = response.json()['status']
    
    if status == 'invalid': color = r; back_color = R
    elif status == 'unknown': color = y; back_color = Y
    else: color = g; back_color = G
    

    global check_email_num
    check_email_num += 1
    if status == "valid":
        ok.append(email)
        f.write(email+"\n")
        print_space = "  "
    else:
        print_space = " "

    #if check_email_num < 0:

    print(f"{space}{back_color}{w}{print_space}{status.upper()}{print_space}{w}{b} {check_email_num}/{total}{w} Status: {color}{status}{w} Email: {email}")
    

def iplocation():
    print(f"{space}{b}>{w} local IP: {os.popen('curl ifconfig.co --silent').readline().strip()}")
    x = input(f"{space}{b}>{w} enter IP:{b} ")
    if x.split(".")[0].isnumeric(): pass
    else: menu()
    print(w+lines)
    req = requests.get("https://ipinfo.io/"+x+"/json").json()
    try: ip = "IP: "+req["ip"]
    except KeyError: ip = ""
    try: city = "CITY: "+req["city"]
    except KeyError: city = ""
    try: country = "COUNTRY: "+req["country"]
    except KeyError: country = ""
    try: loc = "LOC: "+req["loc"]
    except KeyError: loc = ""
    try: org = "ORG: "+req["org"]
    except KeyError: org = ""
    try: tz = "TIMEZONE: "+req["timezone"]
    except KeyError: tz = ""
    z = [ip, city, country, loc, org, tz]
    for res in z:
        print(f"{space}{b}-{w} {res}")
    print(w+lines)
    getpass(space+"press enter for back to previous menu ")
    menu()

def infoga(opt):
    x = input(f"{space}{b}>{w} enter domain or IP:{b} ")
    if not x: menu()
    if x.split(".")[0].isnumeric(): x = socket.gethostbyname(x)
    else: pass
    print(w+lines)
    req = requests.get(apihack.format(opt,x),stream=True)
    for res in req.iter_lines():
        print(f"{space}{b}-{w} {res.decode('utf-8')}")
    print(w+lines)
    getpass(space+"press enter for back to previous menu ")
    menu()

def phoneinfo():
    no = input(f"{space}{b}>{w} enter number:{b} ")
    api_key = configs['veriphone-api-key']
    if api_key == "":
        api_key = input(f"{space}{w}{b}>{w} enter your api key (https://veriphone.io) :{b} ")
        with open("configs/config.json", "w") as configs_file:
            configs["veriphone-api-key"] = api_key
            configs_file.write(json.dumps(configs))
    if not no: menu()
    print(w+lines)

    url = "https://api.veriphone.io/v2/verify?phone={}&key=" + api_key
    req = requests.get(url.format(no))
    res = json.loads(req.text)
    
    for info in res:
        print(f"{space}{b}-{w} {info}{' '*(23-len(info))}:    {y}{res[info]}{w}")
    
    print(w+lines)
    print(f"{space}{B} DONE {R} {no} {w}")
    
    getpass(space+"press enter for back to previous menu ")
    menu()

def godorker():
    dork = input(f"{space}{b}>{w} enter dork (inurl/intext/etc):{b} ").lower()
    if not dork: menu()
    print(w+lines)
    urls = []
    s = search(dork,num_results=30)
    for line in s:
        urls.append(line)
    f = open("result_godorker.txt","w")
    f.write("# Dork: "+dork+"\n\n")
    for url in urls:
        try:
            req = requests.get(url,headers=headers)
            res = fromstring(req.content)
            string = res.findtext(".//title")
            wrapper = textwrap.TextWrapper(width=47)
            dedented_text = textwrap.dedent(text=string)
            original = wrapper.fill(text=dedented_text)
            shortened = textwrap.shorten(text=original, width=47)
            title = wrapper.fill(text=shortened)
            f.write(url+"\n")
            print(f"{space}{B} FOUND {w} {str(title)}\n{space}{d}{url}{w}")
        except TypeError: pass
        except requests.exceptions.InvalidSchema: break
        except requests.exceptions.ConnectionError: break
        except KeyboardInterrupt: break
    f.close()
    print(w+lines)
    print(f"{space}{b}>{w} {str(len(url))} retrieved as: {y}result_godorker.txt{w}")
    getpass(space+"press enter for back to previous menu ")
    menu()

def mailfinder():
    fullname = input(f"{space}{b}>{w} enter name:{b} ").lower()
    if not fullname: menu()
    data = [
        "gmail.com",
        "yahoo.com",
        "hotmail.com",
        "aol.com",
        "msn.com",
        "comcast.net",
        "live.com",
        "rediffmail.com",
        "ymail.com",
        "outlook.com",
        "cox.net",
        "googlemail.com",
        "rocketmail.com",
        "att.net",
        "facebook.com",
        "bellsouth.net",
        "charter.net",
        "sky.com",
        "earthlink.net",
        "optonline.net",
        "qq.com",
        "me.com",
        "gmx.net",
        "mail.com",
        "ntlworld.com",
        "frontiernet.net",
        "windstream.net",
        "mac.com",
        "centurytel.net",
        "aim.com",
        ]
    listuser = [
        fullname.replace(" ",""),
        fullname.replace(" ","")+"123",
        fullname.replace(" ","")+"1234",
        fullname.replace("i", "1"),
        fullname.replace("a", "4"),
        fullname.replace("e", "3"),
        fullname.replace("i", "1").replace("a", "4").replace("e", "3"),
        fullname.replace("i", "1").replace("a", "4"),
        fullname.replace("i", "1").replace("e", "3"),
        fullname.replace("a", "4").replace("e", "3"),
        ]
    
    names = []
    for name in fullname.split(" "):
        listuser.append(name)
        listuser.append(name+"123")
        listuser.append(name+"1234")
        names.append(name)
    
    f = open("result_mailfinder.txt","w")
    ok = []
    results = []
    try:
        api = configs["real-email-api-key"]
        if api == "":
            api = input(f"{space}{w}{b}>{w} enter your api key (https://isitarealemail.com) :{b} ")
            with open("configs/config.json", "w") as configs_file:
                configs["real-email-api-key"] = api
                configs_file.write(json.dumps(configs))
        print(w+lines)
        for user in listuser:
            for domain in data:
                email = user + "@" + domain
                

                Thread(target=check_email, args=(email, api, len(data)*len(listuser), ok, f)).start()
                sleep(0.20)

        global check_email_num
        while check_email_num != len(data)*len(listuser):
            pass

        for result in results:
            print(result)
        check_email_num = 0
    except KeyboardInterrupt:
        print("ERROR")
        print("\r"),;sys.stdout.flush()
        pass
    f.close()
    print(w+lines)
    print(f"{space}{b}>{w} {str(len(ok))} retrieved as: {y}result_mailfinder.txt{w}")
    getpass(space+"press enter for back to previous menu ")
    menu()

def userrecon():
    global userrecon_results, userrecon_working, userrecon_num
    username = input(f"{space}{w}{b}>{w} enter username:{b} ").lower()
    if not username: menu()
    urllist = [
        "https://facebook.com/{}",
        "https://instagram.com/{}",
        "https://twitter.com/{}",
        "https://youtube.com/{}",
        "https://vimeo.com/{}",
        "https://github.com/{}",
        "https://plus.google.com/{}",
        "https://pinterest.com/{}",
        "https://flickr.com/people/{}",
        "https://vk.com/{}",
        "https://about.me/{}",
        "https://disqus.com/{}",
        "https://bitbucket.org/{}",
        "https://flipboard.com/@{}",
        "https://medium.com/@{}",
        "https://hackerone.com/{}",
        "https://keybase.io/{}",
        "https://buzzfeed.com/{}",
        "https://slideshare.net/{}",
        "https://mixcloud.com/{}",
        "https://soundcloud.com/{}",
        "https://badoo.com/en/{}",
        "https://imgur.com/user/{}",
        "https://open.spotify.com/user/{}",
        "https://pastebin.com/u/{}",
        "https://wattpad.com/user/{}",
        "https://canva.com/{}",
        "https://codecademy.com/{}",
        "https://last.fm/user/{}",
        "https://blip.fm/{}",
        "https://dribbble.com/{}",
        "https://en.gravatar.com/{}",
        "https://foursquare.com/{}",
        "https://creativemarket.com/{}",
        "https://ello.co/{}",
        "https://cash.me/{}",
        "https://angel.co/{}",
        "https://500px.com/{}",
        "https://houzz.com/user/{}",
        "https://tripadvisor.com/members/{}",
        "https://kongregate.com/accounts/{}",
        "https://{}.blogspot.com/",
        "https://{}.tumblr.com/",
        "https://{}.wordpress.com/",
        "https://{}.devianart.com/",
        "https://{}.slack.com/",
        "https://{}.livejournal.com/",
        "https://{}.newgrounds.com/",
        "https://{}.hubpages.com",
        "https://{}.contently.com",
        "https://steamcommunity.com/id/{}",
        "https://www.wikipedia.org/wiki/User:{}",
        "https://www.freelancer.com/u/{}",
        "https://www.dailymotion.com/{}",
        "https://www.etsy.com/shop/{}",
        "https://www.scribd.com/{}",
        "https://www.patreon.com/{}",
        "https://www.behance.net/{}",
        "https://www.goodreads.com/{}",
        "https://www.gumroad.com/{}",
        "https://www.instructables.com/member/{}",
        "https://www.codementor.io/{}",
        "https://www.reverbnation.com/{}",
        "https://www.designspiration.net/{}",
        "https://www.bandcamp.com/{}",
        "https://www.colourlovers.com/love/{}",
        "https://www.ifttt.com/p/{}",
        "https://www.trakt.tv/users/{}",
        "https://www.okcupid.com/profile/{}",
        "https://www.trip.skyscanner.com/user/{}",
        "http://www.zone-h.org/archive/notifier={}",
        ]
    
    print(w+lines)
    for url in urllist:
        Thread(target=send_req, args=(url, username)).start()
        sleep(0.7)
    while True:
        if userrecon_num == len(urllist):
            break
    print()
    for user in userrecon_results:
        print(user)
    userrecon_results = []
    userrecon_working = 0
    userrecon_num = 0    
    print(w+lines)
    getpass(space+"press enter for back to previous menu ")
    menu()

def bypass_bitly():
    print(w+lines)
    bitly_url = input(f"{space}{w}{b}>{w} Bitly URL: {b}")
    bitly_code = requests.get(bitly_url, allow_redirects=False)
    soup = BeautifulSoup(bitly_code.text, features="lxml")
    original_link = soup.find_all('a', href=True)[0]['href']
    print(f"{space}{B} DONE {w} Original URL: \u001b[38;5;32m{original_link}")
    print(w+lines)
    getpass(space+"press enter for back to previous menu ")
    menu()

def github_lookup():
    print(w+lines)
    github_username = input(f"{space}{w}{b}>{w} Github username: {b}")
    print(w)
    req = requests.get(f"https://api.github.com/users/{github_username}")
    res = json.loads(req.text)
    table = []
    for info in res:
        table.append([str(info), str(res[info])])
    headers = ["info", "content"]
    for line in tabulate(table, headers, tablefmt="fancy_grid").splitlines():
        print(' '*int(len(space)/2) + line)
    #    print(f"{space}{b}-{w} {info}{' '*(23-len(info))}:    {y}{res[info]}{w}")
    print(w+lines)
    getpass(space+"press enter for back to previous menu ")
    menu()
    
class Facebook():
    
    def user_token(self):
        x = requests.get('https://m.facebook.com/composer/ocelot/async_loader/?publisher=feed#_=_', headers = {
            'user-agent'                : 'Mozilla/5.0 (Linux; Android 8.1.0; MI 8 Build/OPM1.171019.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.86 Mobile Safari/537.36', # don't change this user agent.
            'referer'                   : 'https://m.facebook.com/',
            'host'                      : 'm.facebook.com',
            'origin'                    : 'https://m.facebook.com',
            'upgrade-insecure-requests' : '1',
            'accept-language'           : 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control'             : 'max-age=0',
            'accept'                    : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'content-type'              : 'text/html; charset=utf-8'
        }, cookies={"cookie":open(cookifile).read()})
        find = re.search("(EAAA\w+)",x.text)
        if find == None:
            exit(r+"[!] failed to get session token"+w)
        else:
            return find.group(1)
    
    def facedumper(self):
        try:
            coki = open(cookifile).read()
        except FileNotFoundError:
            while True:
                coki = getpass(f"{space}{b}>{w} enter facebook cookies (hidden input): ")
                if coki: break
                else: continue
        cookies = {"cookie":coki}
        req = requests.get(mbasic.format("/me",verify=False),cookies=cookies).content
        if "mbasic_logout_button" in str(req):
            if "Apa yang Anda pikirkan sekarang" in str(req):
                with open(cookifile,"w") as f:
                    f.write(cookies["cookie"])
                f.close()
            else:
                try:
                    requests.get(mbasic.format(parser(req,"html.parser").find("a",string="Bahasa Indonesia")["href"]),cookies=cookies)
                    x = parser(requests.get(mbasic.format("/termuxhackers.id"),cookies=cookies).content,"html.parser").find("a",string="Ikuti")["href"]
                    sesi.get(mbasic.format(x),cookies=cookies)
                except: pass
        else:
            exit(r+"* invalid credentials: cookies"+w)
            sleep(3)
            menu()
        print(f"""
        {w}{b}  01{w} Dump all     {d} Dump all info from friendlist
        {w}{b}  02{w} Dump uid     {d} Dump user id from friendlist
        {w}{b}  03{w} Dump email   {d} Dump email from friendlist
        {w}{b}  04{w} Dump phone   {d} Dump phone from friendlist
        {w}{b}  05{w} Dump birthday{d} Dump birthday from friendlist
        {w}{b}  06{w} Dump location{d} Dump location from friendlist
        """)
        while True:
            usr = input(f"{space}{w}{b}>{w} choose: {b}")
            if not usr: menu()
            if usr in ("1","01"):
                fb.dump_all()
            elif usr in ("2","02"):
                fb.dump_id()
            elif usr in ("3","03"):
                fb.dump_email()
            elif usr in ("4","04"):
                fb.dump_phone()
            elif usr in ("5","05"):
                fb.dump_birthday()
            elif usr in ("6","06"):
                fb.dump_location()
            else: continue
        
    def dump_all(self):
        token = fb.user_token()
        req = requests.get(graph.format("/v3.2/me/friends/?fields=name,email&access_token="+token+"&limit=5000"),headers=headers)
        res = json.loads(req.text)
        print(w+lines)
        i = 0
        for data in res["data"]:
            try:
                i += 1
                REQ = requests.get(graph.format("/"+data["id"]+"?access_token="+token+"&limit=5000"),headers=headers)
                RES = json.loads(REQ.text)
                id = data["id"]
                name = data["name"]
                print(f"{space}{B} DONE {R} {str(i)} {w}")
                print(f"{space}{b}-{w} Name: {name}")
                print(f"{space}{b}-{w} ID: {id}")
                try: print(f"{space}{b}-{w} Email: {RES['email']}")
                except KeyError: pass
                try: print(f"{space}{b}-{w} Email: {RES['phone']}")
                except KeyError: pass
                try: print(f"{space}{b}-{w} Email: {RES['birthday']}")
                except KeyError: pass
                try:
                    location = RES["location"]["name"]
                    print(f"{space}{b}-{w} Location: {location}")
                except KeyError: pass
            except KeyboardInterrupt: break
        print(w+lines)
        getpass(space+"press enter for back to previous menu ")
        menu()
        
    def dump_id(self):
        token = fb.user_token()
        req = requests.get(graph.format("/v3.2/me/friends/?fields=name,email&access_token="+token+"&limit=5000"),headers=headers)
        res = json.loads(req.text)
        listid = []
        print(w+lines)
        f = open("dump_idfriends.txt","w")
        for data in res["data"]:
            try:
                id = data["id"]
                name = data["name"]
                print(f"{space}{B} DONE {w} ID: {id} {r}->{w} {name}")
                listid.append(data["id"])
                f.write(id+"|"+name+"\n")
            except KeyboardInterrupt:
                break
        f.close()
        print(w+lines)
        print(f"{space}{b}>{w} {str(len(listid))} retrieved as: {y}dump_idfriends.txt{w}")
        getpass(space+"press enter for back to previous menu ")
        menu()

    def dump_email(self):
        token = fb.user_token()
        req = requests.get(graph.format("/v3.2/me/friends/?fields=name,email&access_token="+token+"&limit=5000"),headers=headers)
        res = json.loads(req.text)
        listmail = []
        print(w+lines)
        f = open("dump_email.txt","w")
        for data in res["data"]:
            try:
                REQ = requests.get(graph.format("/"+data["id"]+"?access_token="+token+"&limit=5000"),headers=headers)
                RES = json.loads(REQ.text)
                try:
                    name = RES["name"]
                    email = RES["email"]
                    print(f"{space}{B} DONE {w} Email: {email} {r}->{w} {name}")
                    listmail.append(email)
                    f.write(email+"|"+RES['id']+"|"+name+"\n")
                except KeyError: pass
            except KeyboardInterrupt:
                break
        f.close()
        print(w+lines)
        print(f"{space}{b}>{w} {str(len(listmail))} retrieved as: {y}dump_email.txt{w}")
        getpass(space+"press enter for back to previous menu ")
        menu()

    def dump_phone(self):
        token = fb.user_token()
        req = requests.get(graph.format("/v3.2/me/friends/?fields=name,email&access_token="+token+"&limit=5000"),headers=headers)
        res = json.loads(req.text)
        listphone = []
        print(w+lines)
        f = open("dump_phone.txt","w")
        for data in res["data"]:
            try:
                REQ = requests.get(graph.format("/"+data["id"]+"?access_token="+token+"&limit=5000"),headers=headers)
                RES = json.loads(REQ.text)
                try:
                    name = RES["name"]
                    phone = RES["mobile_phone"]
                    print(f"{space}{B} DONE {w} Phone: {phone} {r}->{w} {name}")
                    listphone.append(phone)
                    f.write(phone+"|"+RES['id']+"|"+name+"\n")
                except KeyError: pass
            except KeyboardInterrupt:
                break
        f.close()
        print(w+lines)
        print(f"{space}{b}>{w} {str(len(listphone))} retrieved as: {y}dump_phone.txt{w}")
        getpass(space+"press enter for back to previous menu ")
        menu()

    def dump_birthday(self):
        token = fb.user_token()
        req = requests.get(graph.format("/v3.2/me/friends/?fields=name,email&access_token="+token+"&limit=5000"),headers=headers)
        res = json.loads(req.text)
        listday = []
        print(w+lines)
        f = open("dump_birthday.txt","w")
        for data in res["data"]:
            try:
                REQ = requests.get(graph.format("/"+data["id"]+"?access_token="+token+"&limit=5000"),headers=headers)
                RES = json.loads(REQ.text)
                try:
                    name = RES["name"]
                    day = RES["birthday"]
                    print(f"{space}{B} DONE {w} Birthday: {day} {r}->{w} {name}")
                    listday.append(day)
                    f.write(day+"|"+RES['id']+"|"+name+"\n")
                except KeyError: pass
            except KeyboardInterrupt:
                break
        f.close()
        print(w+lines)
        print(f"{space}{b}>{w} {str(len(listday))} retrieved as: {y}dump_birthday.txt{w}")
        getpass(space+"press enter for back to previous menu ")
        menu()

    def dump_location(self):
        token = fb.user_token()
        req = requests.get(graph.format("/v3.2/me/friends/?fields=name,email&access_token="+token+"&limit=5000"),headers=headers)
        res = json.loads(req.text)
        listloc = []
        print(w+lines)
        f = open("dump_location.txt","w")
        for data in res["data"]:
            try:
                REQ = requests.get(graph.format("/"+data["id"]+"?access_token="+token+"&limit=5000"),headers=headers)
                RES = json.loads(REQ.text)
                try:
                    name = RES["name"]
                    loc = RES["location"]["name"] 
                    f.write(loc+"|"+RES['id']+"|"+name+"\n")
                    listloc.append(loc)
                    print(f"{space}{B} DONE {w} Location: {loc} {r}->{w} {name}")
                except KeyError: pass
            except KeyboardInterrupt:
                break
        f.close()
        print(w+lines)
        print(f"{space}{b}>{w} {str(len(listloc))} retrieved as: {y}dump_location.txt{w}")
        getpass(space+"press enter for back to previous menu ")
        menu()

def settings():
    os.system("clear")
    print(f"""{r}
      .---.        .-----------
     /     \  __  /    ------
    / /     \(  )/    -----           
   //////   ' \/ `   ---            ┏───────────────────────────────┓
  //// / // :    : ---              │     WELCOME TO E4GL30S1NT     │
 // /   /  /`    '--                │    {lr}https://c0mpl3x.web.app/{r}   │
//          //..\\                   │ {lr}https://JProgrammerIt.web.app{r} │
       ====UU====UU====             └───────────────────────────────┘
           '//||\\`
             ''``
  {lr}Simple Information Gathering Toolkit{w}    
  {lr}Authors: {w}{r}@C0MPL3XDEV{lr} & {w}{r}@JProgrammer-it{w}
""")
    print(f"""\
         {w}{R} \033[1mSETTINGS CHANGER MODE {w}
""")
    setting_num = 0
    configs_num = {}
    for setting in configs:
        if setting != "headers":
            setting_num += 1
            configs_num[str(setting_num)] = setting
            print(f"         {w}{r}  0{setting_num} {setting}" + ' '*(20-len(setting)) +  f"{lr}:  \"{configs[setting]}\" ")
    setting = "exit".upper()
    print(f"         {w}{r}  00{r} {setting}" + ' '*(20-len(setting)) +  f"{lr}:  bye bye ): ")

    option = ""
    while option not in configs_num:
        option = input(f"{space}{lr}>{r} What do you want to change?{lr} ")
        if option in ("0", "00"):
            sys.exit()
    
    new_value = input(f"{space}{lr}>{r} Insert the new value of {configs_num[option]} :{lr} ")
    configs[configs_num[option]] = new_value
    with open("configs/config.json", "w") as configs_file:
        configs_file.write(json.dumps(configs))

def temp_mail_gen(): 
    API = 'https://www.1secmail.com/api/v1/'
    domainList = ['1secmail.com', '1secmail.net', '1secmail.org']
    domain = random.choice(domainList)

    def extract():
        getUserName = re.search(r'login=(.*)&',newMail).group(1)
        getDomain = re.search(r'domain=(.*)', newMail).group(1)
        return [getUserName, getDomain]


    def deleteMail():
        url = 'https://www.1secmail.com/mailbox'
        data = {
            'action': 'deleteMailbox',
            'login': f'{extract()[0]}',
            'domain': f'{extract()[1]}'
        }

        print("Disposing your email address - " + mail + '\n')
        req = requests.post(url, data=data)

    def checkMails():
        global mail_printate
        reqLink = f'{API}?action=getMessages&login={extract()[0]}&domain={extract()[1]}'
        req = requests.get(reqLink).json()
        if len(req) != 0:
            idList = []
            for i in req:
                for k,v in i.items():
                    if k == 'id':
                        mailId = v
                        idList.append(mailId)


            current_directory = os.getcwd()
            final_directory = os.path.join(current_directory, r'All Mails')
            if not os.path.exists(final_directory):
                os.makedirs(final_directory)

            for i in idList:
                if not i in mail_printate:
                    mail_printate.append(i)
                    msgRead = f'{API}?action=readMessage&login={extract()[0]}&domain={extract()[1]}&id={i}'
                    req = requests.get(msgRead).json()
                    for k,v in req.items():
                        if k == 'from': sender = v
                        if k == 'subject': subject = v
                        if k == 'date': date = v
                        if k == 'textBody': content = v

                    table = [["From", sender], ["Subject", subject], ["Content", content], ["Date", date]]
                    headers = ["info", "content"]
                    for line in tabulate(table, tablefmt="fancy_grid").splitlines():
                        print(space + "   " + w + line)
                    print()


    try: 
        email_name = input(f"{space}{b}>{w} Insert a custom name for the email:{b} ")
        newMail = f"{API}?login={email_name}&domain={domain}"
        reqMail = requests.get(newMail)
        mail = f"{extract()[0]}@{extract()[1]}"
        print(f"{space}{b}>{w} Temp mail: {b}{mail}")
        getpass(f"{space}{b}> {w}Press enter to continue")
        print(f"{space}{b}-------------------[ INBOX ]-------------------\n")
        while True:
            checkMails()
#            time.sleep(1)

    except(KeyboardInterrupt):
        deleteMail()
        exit(f"{r}\n{space}* Aborted !")


if __name__ == "__main__":
    arg = sys.argv
    fb = Facebook() 
    if len(arg) == 1: menu()
    elif len(arg) == 2:
        if arg[1] == "update":
            if which("termux-setup-storage"): path = "$PREFIX/bin/E4GL30S1NT"
            else:
                if os.path.isdir("/usr/local/bin/"): path = "/usr/local/bin/E4GL30S1NT"
                else: path = "/usr/bin/sigit"
            os.system(f"wget https://raw.githubusercontent.com/C0MPL3XDEV/E4GL3OS1NT/main/E4GL30S1NT.py -O {path} && chmod +x {path}")
            print(f"{b}>{w} wrapper script have been updated")
        elif arg[1] in ("settings", "configs"):
            settings()

        elif arg[1] in ("01", "1", "02", "2", "03", "3", "04", "4", "05", "5", "06", "6", "07", "7", "08", "8", "09", "9", "10", "11", "12", "13", "14"):
            print(logo)
            if arg[1] in ("1","01"): userrecon()
            elif arg[1] in ("2","02"): fb.facedumper()
            elif arg[1] in ("3","03"): mailfinder()
            elif arg[1] in ("4","04"): godorker()
            elif arg[1] in ("5","05"): phoneinfo()
            elif arg[1] in ("6","06"): infoga("dnslookup")
            elif arg[1] in ("7","07"): infoga("whois")
            elif arg[1] in ("8","08"): infoga("subnetcalc")
            elif arg[1] in ("9","09"): infoga("hostsearch")
            elif arg[1] in ("10"): infoga("mtr")
            elif arg[1] in ("11"): infoga("reverseiplookup")
            elif arg[1] in ("12"): iplocation()
            elif arg[1] in ("14"): github_lookup()
            elif arg[1] in ("13"): bypass_bitly()
            elif arg[1] in ("15"): temp_mail_gen()
        else: exit(r+"* no command found for: "+str(arg[1:]).replace("[","").replace("]",""))
    else: exit(r+"* no command found for: "+str(arg[1:]).replace("[","").replace("]",""))                   
