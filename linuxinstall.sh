#! /usr/bin/bash
null="> /dev/null 2>&1"
g="\033[1;32m"
r="\033[1;31m"
b="\033[1;34m"
w="\033[0m"
echo -e "$b"">""$w"" E4GL30SINT - Simple information gathering toolkit"
echo -e "$b"">""$w"" prepare for installing dependencies ..."
sleep 3
echo -e "$b"">""$w"" installing package: ""$g""libxml2""$w"
sudo apt install libxml2 -y
echo -e "$b"">""$w"" installing pacakge: ""$g""libxslt""$w"
sudo apt install libxslt1.1 -y
echo -e "$b"">""$w"" installing pacakge: ""$g""python3""$w"
sudo apt install python3 python-is-python3 -y
echo -e "$b"">""$w"" installing package: ""$g""python3-pip""$w"
sudo apt install python3-pip -y
echo -e "$b"">""$w"" installing modules: ""$g""lxml""$w"
sudo apt install python3-lxml python3-wheel -y
echo -e "$b"">""$w"" installing modules: ""$g""requests""$w"
sudo apt install python3-requests -y
echo -e "$b"">""$w"" installing modules: ""$g""BeautifulSoup""$w"
sudo apt install python3-bs4 -y
echo -e "$b"">""$w"" installing modules: ""$g""tabuate""$w"
sudo apt install python3-tabulate -y
echo -e "$b"">""$w"" successfully installing dependencies"
sudo wget -q https://raw.githubusercontent.com/C0MPL3XDEV/E4GL3OS1NT/main/E4GL30S1NT.py -O /usr/local/bin/E4GL30S1NT && sudo chmod +x /usr/local/bin/E4GL30S1NT
echo -e "$b"">""$w"" use command ""$g""E4GL30S1NT""$w"" for start the console"
