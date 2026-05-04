#!/usr/bin/env bash

g="\033[1;32m"
r="\033[1;31m"
b="\033[1;34m"
w="\033[0m"

APP_NAME="E4GL30S1NT"
APP_URL="https://raw.githubusercontent.com/C0MPL3XDEV/E4GL3OS1NT/main/E4GL30S1NT.py"
INSTALL_PATH="/usr/local/bin/$APP_NAME"

echo -e "$b> $w $APP_NAME - Simple information gathering toolkit"
echo -e "$b> $w Preparing to install dependencies..."
sleep 3

detect_package_manager() {
    if command -v apt >/dev/null 2>&1; then
        echo "apt"
    elif command -v pacman >/dev/null 2>&1; then
        echo "pacman"
    elif command -v dnf >/dev/null 2>&1; then
        echo "dnf"
    else
        echo "unknown"
    fi
}

install_dependencies() {
    pm="$(detect_package_manager)"

    case "$pm" in
        apt)
            echo -e "$b> $w Detected Debian/Ubuntu-based system"

            echo -e "$b> $w Updating package database..."
            sudo apt update

            echo -e "$b> $w Installing dependencies..."
            sudo apt install -y \
                libxml2 \
                libxslt1.1 \
                python3 \
                python-is-python3 \
                python3-pip \
                python3-lxml \
                python3-wheel \
                python3-requests \
                python3-bs4 \
                python3-tabulate \
                wget

            echo -e "$b> $w Installing module: $g pyperclip $w"
            if ! sudo apt install -y python3-pyperclip; then
                echo -e "$r[!] apt install failed, trying pip3...$w"
                pip3 install --user pyperclip
            fi
            ;;

        pacman)
            echo -e "$b> $w Detected Arch-based system"

            echo -e "$b> $w Installing dependencies..."
            sudo pacman -Syu --needed --noconfirm \
                libxml2 \
                libxslt \
                python \
                python-pip \
                python-lxml \
                python-wheel \
                python-requests \
                python-beautifulsoup4 \
                python-tabulate \
                python-pyperclip \
                wget
            ;;

        dnf)
            echo -e "$b> $w Detected Fedora-based system"

            echo -e "$b> $w Installing dependencies..."
            sudo dnf install -y \
                libxml2 \
                libxslt \
                python3 \
                python3-pip \
                python3-lxml \
                python3-wheel \
                python3-requests \
                python3-beautifulsoup4 \
                python3-tabulate \
                python3-pyperclip \
                wget
            ;;

        *)
            echo -e "$r[!] Unsupported system. Could not find apt, pacman, or dnf.$w"
            exit 1
            ;;
    esac
}

install_tool() {
    echo -e "$b> $w Downloading $g $APP_NAME $w"

    sudo wget -q "$APP_URL" -O "$INSTALL_PATH"
    sudo chmod +x "$INSTALL_PATH"

    if ! head -n 1 "$INSTALL_PATH" | grep -q '^#!'; then
        echo -e "$b> $w Adding Python shebang..."
        tmpfile="$(mktemp)"
        echo '#!/usr/bin/env python3' > "$tmpfile"
        sudo cat "$INSTALL_PATH" >> "$tmpfile"
        sudo mv "$tmpfile" "$INSTALL_PATH"
        sudo chmod +x "$INSTALL_PATH"
    fi
}

install_dependencies

echo -e "$b> $w Successfully installed dependencies"

install_tool

echo -e "$b> $w Use command $g $APP_NAME $w to start the console"
