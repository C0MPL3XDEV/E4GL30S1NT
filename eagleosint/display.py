"""ANSI color constants, layout helpers, progress bar, and ASCII logo."""

# Colors
RED       = "\033[31m"
GREEN     = "\033[32m"
YELLOW    = "\033[33m"
BLUE      = "\033[34m"
PURPLE    = "\033[35m"
DARK_GRAY = "\033[2;37m"
WHITE     = "\033[0m"
LIGHT_RED = "\u001b[38;5;196m"

# Background colors
BG_WHITE  = f"{WHITE}\033[1;47m"
BG_RED    = f"{WHITE}\033[1;41m"
BG_GREEN  = f"{WHITE}\033[1;42m"
BG_YELLOW = f"{WHITE}\033[1;43m"
BG_BLUE   = f"{WHITE}\033[1;44m"

SPACE_PREFIX   = "         "
LINES_SEPARATOR = SPACE_PREFIX + "-" * 44

LOGO = f"""{BLUE}
      .---.        .-----------
     /     \\  __  /    ------
    / /     \\(  )/    -----
   //////   ' \\/ `   ---            ┏───────────────────────────────┓
  //// / // :    : ---              │     WELCOME TO E4GL30S1NT     │
 // /   /  /`    '--                │     https://carminedev.it     │
//          //..\\                   │     https://sgrodolix.website │
       ====UU====UU====             └───────────────────────────────┘
           '//||\\`
             ''``
  {DARK_GRAY}Simple Information Gathering Toolkit{WHITE}
  {DARK_GRAY}Authors: {WHITE}{RED}@C0MPL3XDEV{DARK_GRAY} & {WHITE}{RED}@JProgrammer-it{WHITE}
"""


def display_progress(iteration, total, text=""):
    """Displays a progress bar in the console."""
    bar_max_width = 40
    bar_current_width = int(bar_max_width * iteration / total)
    progress_bar = "█" * bar_current_width + " " * (bar_max_width - bar_current_width)
    progress_percentage = f"{(iteration / total * 100):.1f}"
    print(
        f"{SPACE_PREFIX}{iteration}/{total} |{progress_bar}| {progress_percentage}% {text}",
        end="\r",
    )
    if iteration == total:
        print()