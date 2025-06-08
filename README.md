<h1 align="center">E4GL30S1NT</h1>

<img src="https://github.com/C0MPL3XDEV/E4GL30S1NT/blob/main/image/imageonline-co-roundcorner.png">
<p align="center">
<a href="https://discord.gg/Vy8C724XWV"><img src="https://discordapp.com/api/guilds/437716353584070677/widget.png?style=shield" alt="Discord Server"></a>


<br>

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)


<img title="E4GL30S1NT" src="https://img.shields.io/badge/CODENAME%20-E4GL30S1NT-E4GL30S1NT?colorA=grey&colorB=green&style=for-the-badge"> <img title="E4GL30S1NT" src="https://img.shields.io/badge/VERSION%20-1.1-SCRIPT?colorA=grey&colorB=green&style=for-the-badge"> <img src="https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white">
<img src="https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white"/>


<img src="https://github.com/C0MPL3XDEV/E4GL30S1NT/blob/main/image/Screenshot_2.png">

### Features
- ```userrecon```    - username reconnaissance
- ```facedumper```   - dump facebook information
- ```mailfinder``` - find email with specific name
- ```godorker``` - dorking with google search
- ```phoneinfo``` - phone number information
- ```dnslookup``` - domain name system lookup
- ```whoislookup``` - identify who is on domain
- ```sublookup``` - sub networking lookup
- ```hostfinder``` - find host domain
- ```dnsfinder``` - find host domain name system
- ```riplookup``` - reverse ip lookup
- ```iplocation``` - ip to location tracker
- ```Bitly Bypass``` - Bypass all bitly urls 
- ```Github Lookup``` -  Dump GitHub information 
- ```TempMail``` - Generate a Temp Mail and Mail Box 

### USE:
  - For Put or Modify API KEY Type ```python3 E4GL30S1NT.py configs``` or edit configs/config.json
  - For use ```phoneinfo``` you need a [Veriphone API key](https://veriphone.io/), if you don't have this key you can use this test key to test the tool: KEY: ```47703D994B174BACBDC5AD734CC381B4```
  - For use ```mailfinder``` you need a [real-email API key](https://isitarealemail.com/), if you don't have this key you can use this test key to test the tool: KEY: ```0c6ad1fd-f753-4628-8c0a-7968e722c6c7```

- Installation on linux
```bash
sudo apt-get install wget && wget https://raw.githubusercontent.com/C0MPL3XDEV/E4GL30S1NT/main/linuxinstall.sh && bash linuxinstall.sh
```

- Installation on termux
```bash
pkg install wget && https://raw.githubusercontent.com/C0MPL3XDEV/E4GL30S1NT/main/install.sh && bash install.sh
```
- Uninstallation
- termux: ```rm -rf $PREFIX/bin/E4GL30S1NT```
- linux  : ```rm -rf /usr/local/bin/E4GL30S1NT```

## Setup and Dependencies

To ensure all necessary Python packages and type stubs are installed for `E4GL30S1NT.py`, please run the provided shell script:

First, make sure the script is executable:
\`\`\`bash
chmod +x install_deps.sh
\`\`\`

Then, run the script:
\`\`\`bash
./install_deps.sh
\`\`\`

This script will:
1. Install core runtime libraries listed in `requirements.txt`.
2. Install `types-botocore` and `types-boto3` as per user preference.
3. Run `mypy --install-types` to fetch other necessary type stubs for `E4GL30S1NT.py`.

## Debugging

This script includes an example for using `debugpy` to debug its execution. To use it:

1.  Ensure `debugpy` is installed. You can install it using pip:
    \`\`\`bash
    pip install debugpy
    \`\`\`
    (The `install_deps.sh` script also attempts to install type stubs via `mypy`, which might include `debugpy` if it's imported and type stubs are available).
2.  In the `E4GL30S1NT.py` script, find the `if __name__ == "__main__":` block.
3.  Uncomment the section related to `debugpy` setup.
4.  Run the script. It will print a message and pause, waiting for a debugger to attach on port 5678 (or the configured port).
5.  Attach your Python debugger (e.g., from VS Code, PyCharm) to the specified port.

### Credits
Copyright © 2023 by <a href="https://www.instagram.com/c0mpl3xdev/">@C0MPL3XDEV</a> <a href="https://github.com/PoulDev">@PoulDev</a>
