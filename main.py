if __name__ != "__main__":
    exit()

import curses

import random
import time

import argparse

from engine import Wordle
from bot import Bot

def parse_args():
    parser = argparse.ArgumentParser(description="RE:Word - A puzzle game where you try to figure out what a wordle bot guessed to reach a certain answer.")

    parser.add_argument(
        "--puzzle", type=str, default=None,
        help="Start a specific puzzle with a specific endpoint."
    )

    parser.add_argument(
        "--seed", type=int, default=None,
        help="Specify an RNG seed for the bot."
    )

    parser.add_argument(
        "--time", type=int, default=300,
        help="Specify how much time you have to solve the puzzle."
    )

    return parser.parse_args()

args = parse_args()

words = open('words.txt', 'r').read().splitlines()
all_words = words.copy()

if args.seed is not None:
    seed = args.seed
else: 
    seed = random.randint(0, pow(2, 16) - 1)

while True:
    random.seed(seed)
    words = all_words.copy()
    random.shuffle(words)
    engine = Wordle(words.pop() if args.puzzle is None or args.puzzle.lower().strip() not in all_words else args.puzzle.lower().strip())
    bot = Bot(words.pop(), engine)
    bot.solve()
    if bot.guesses[-1][1] == "GGGGG":
        break

width, height = 30, 15

def main(stdscr: curses.window):
    curses.start_color()
    curses.echo()
    curses.curs_set(0)

    stdscr.nodelay(True)
    stdscr.resize(height + 2, width + 2)

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK    )
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK  )
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK   )
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK )
    curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK   )
    curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    class Colors:
        WHITE = curses.color_pair(0)
        RED = curses.color_pair(1)
        GREEN = curses.color_pair(2)
        BLUE = curses.color_pair(3)
        YELLOW = curses.color_pair(4)
        CYAN = curses.color_pair(5)
        MAGENTA = curses.color_pair(6)

    input_string = ""

    player_guesses = ["?????" for _ in range(len(bot.guesses))]
    player_guesses[-1] = bot.guesses[-1][0]

    timer = min(max(15.0, args.time), 1000.0)
    max_time = timer

    prev_time = time.time()

    show_text = ""

    idx = 0

    while True:
        try:
            if timer < 0:
                show_text = f"Sorry! You failed to finsih\nthis puzzle in time. Your\npuzzle was \"{bot.guesses[-1][0]}\" and your\nseed was {seed}. Press any\nkey to exit."
                break

            stdscr.clear()
            stdscr.box()

            stdscr.addstr(0, 1, "RE:Word")

            if max_time - timer <= 10.0:
                stdscr.addstr(1, 1, "what to enter to play:")
                stdscr.addstr(2, 1, "<ENTRY NO.> + [SPACE] + <WORD>")

            try:
                stdscr.addstr(height, 1, input_string + ('█' if int(timer * 2) & 1 else ' '))
            except:
                input_string = ""

            all_correct = True

            ox = width // 2 - 3
            oy = 3
            for i, (guess, seq) in enumerate(bot.guesses):
                if i == idx:
                    stdscr.addstr(oy + i * 2 + 0, ox - 2, '> ')
                stdscr.addstr(oy + i * 2 + 0, ox, str(i + 1) + ' ')
                col = Colors.GREEN if player_guesses[i] == guess else Colors.RED
                new_seq = engine.sequence(player_guesses[i], guess)
                count = new_seq.count('G')
                if count >= 3 and count < 5:
                    col = Colors.YELLOW
                if col != Colors.GREEN:
                    all_correct = False
                stdscr.addstr(oy + i * 2 + 0, ox + 2, player_guesses[i], col)
                for j, char in enumerate(seq):
                    stdscr.addch(oy + i * 2 + 1, ox + j + 2, '•', {
                        '_': Colors.RED,
                        'Y': Colors.YELLOW,
                        'G': Colors.GREEN
                    }[char])

            if all_correct:
                show_text = f"You won! This puzzle took you\n{max_time - timer:.1f} seconds. Your puzzle\nwas \"{bot.guesses[-1][0]}\" and your seed\nwas {seed}. Press any\nkey to exit."
                break

            t = time.time()
            delta = t - prev_time
            timer -= delta
            s = f"{timer:.1f}s"
            stdscr.addstr(height, width - len(s) + 1, s)

            stdscr.refresh()

            stdscr.move(height, 1)
            key = stdscr.getch()
            if key != -1:
                if key in (curses.KEY_ENTER, 10, 13):
                    input_string = input_string.strip()
                    if len(input_string):
                        if input_string[0] in "12345":
                            idx = int(input_string[0]) - 1
                            if 0 <= idx < len(player_guesses) - 1:
                                if len(input_string.split(' ')) == 2:
                                    g = input_string.split(' ')[1]
                                    if len(g) == 5 and g.isalpha() and g.lower() in all_words:
                                        player_guesses[idx] = g.lower()
                        else:
                            g = input_string.strip()
                            if len(g) == 5 and g.isalpha() and g.lower() in all_words:
                                player_guesses[idx] = g.lower()
                    input_string = ""
                elif key in (curses.KEY_BACKSPACE, 127, 8):
                    input_string = input_string[:-1]
                elif 0 <= key <= 255 and len(input_string) < 12:
                    if chr(key).isalnum() or chr(key) in ' ':
                        input_string += chr(key)

            prev_time = t
        except KeyboardInterrupt:
            return
    
    while True:
        try:
            stdscr.clear()
            stdscr.box()

            stdscr.addstr(0, 1, "RE:Word")

            y = 5
            for line in show_text.splitlines():
                try:
                    stdscr.addstr(y, width // 2 - len(line) // 2, line)
                except:
                    continue
                y += 1

            stdscr.refresh()

            key = stdscr.getch()
            if key != -1:
                break
        except KeyboardInterrupt:
            return

curses.wrapper(main)