"""Delicate — Taylor Swift:

    python delicate.py
    python delicate.py --from-start
    python delicate.py --preview
    python delicate.py --offset 0.3

"""

import argparse
import bisect
import math
import os
import re
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple


TITLE = "Delicate"
ARTIST = "Taylor Swift"

EMBEDDED_LRC = "[id: ngirbor5]\n[ar: Taylor Swift]\n[al: reputation]\n[ti: Delicate]\n[length: 03:52]\n\n[00:00.72]This <00:00.93>ain't <00:01.13>for <00:01.35>the <00:01.52>best\n[00:02.68]My <00:03.00>reputation's <00:03.98>never <00:04.29>been <00:04.65>worse, <00:04.93>so\n[00:05.82]You <00:06.02>must <00:06.17>like <00:06.47>me <00:06.79>for <00:07.09>me\n[00:11.08]We <00:11.26>can't <00:11.60>make\n[00:12.71]Any <00:13.06>promises <00:13.73>now, <00:14.06>can <00:14.38>we, <00:14.69>babe?\n[00:15.76]But <00:15.93>you <00:16.11>can <00:16.30>make <00:16.61>me <00:16.93>a <00:17.25>drink\n[00:17.93]\n[00:20.27]Dive <00:20.67>bar <00:21.02>on <00:21.21>the <00:21.36>East <00:21.64>Side, <00:21.88>where <00:22.08>you <00:22.28>at?\n[00:22.88]Phone <00:23.02>lights <00:23.55>up <00:23.73>my <00:23.88>nightstand <00:24.51>in <00:24.68>the <00:24.84>black\n[00:25.43]Come <00:25.75>here, <00:26.10>you <00:26.26>can <00:26.42>meet <00:26.68>me <00:27.05>in <00:27.21>the <00:27.38>back\n[00:30.48]Dark <00:30.77>jeans <00:31.13>and <00:31.32>your <00:31.49>Nikes, <00:32.09>look <00:32.25>at <00:32.47>you\n[00:33.01]Oh <00:33.31>damn, <00:33.64>never <00:33.98>seen <00:34.29>that <00:34.59>color <00:34.94>blue\n[00:35.54]Just <00:35.87>think <00:36.20>of <00:36.39>the <00:36.53>fun <00:36.83>things <00:37.14>we <00:37.30>could <00:37.47>do\n[00:39.57]'Cause <00:39.80>I <00:39.98>like <00:40.92>you\n[00:42.70]\n[00:41.16]This <00:41.39>ain't <00:41.57>for <00:41.73>the <00:41.90>best\n[00:43.04]My <00:43.41>reputation's <00:44.39>never <00:44.68>been <00:45.02>worse, <00:45.34>so\n[00:46.19]You <00:46.38>must <00:46.58>like <00:46.88>me <00:47.20>for <00:47.51>me\n[00:49.71]Yeah, <00:49.93>I <00:50.23>want <00:51.03>you\n[00:51.42]We <00:51.64>can't <00:51.98>make\n[00:53.24]Any <00:53.51>promises <00:54.18>now, <00:54.51>can <00:54.81>we, <00:55.16>babe?\n[00:56.22]But <00:56.39>you <00:56.56>can <00:56.74>make <00:57.02>me <00:57.34>a <00:57.67>drink\n[00:58.21]\n[01:00.45]Is <01:00.67>it <01:00.82>cool <01:01.12>that <01:01.27>I <01:01.47>said <01:01.77>all <01:02.12>that?\n[01:02.99]Is <01:03.19>it <01:03.35>chill <01:03.65>that <01:03.84>you're <01:04.01>in <01:04.29>my <01:04.57>head?\n[01:05.49]'Cause <01:05.68>I <01:05.88>know <01:06.19>that <01:06.37>it's <01:06.55>deli<01:07.16>cate\n[01:10.53]Is <01:10.74>it <01:10.95>cool <01:11.26>that <01:11.44>I <01:11.62>said <01:11.88>all <01:12.19>that?\n[01:13.10]Is <01:13.25>it <01:13.45>too <01:13.72>soon <01:13.89>to <01:14.04>do <01:14.36>this <01:14.74>yet?\n[01:15.62]'Cause <01:15.78>I <01:15.97>know <01:16.30>that <01:16.48>it's <01:16.67>deli<01:17.27>cate\n[01:19.81]Isn't <01:20.03>it? <01:20.39>Isn't <01:20.69>it? <01:21.04>Isn't <01:21.31>it?\n[01:22.83]Isn't <01:23.17>it?\n[01:24.72]Isn't <01:25.09>it? <01:25.44>Isn't <01:25.74>it? <01:26.07>Isn't <01:26.37>it?\n[01:27.95]Isn't <01:28.23>it <01:29.16>delicate?\n[01:30.34]\n[01:31.07]Third <01:31.40>floor <01:31.79>on <01:31.94>the <01:32.12>West <01:32.42>Side, <01:32.76>me <01:32.92>and <01:33.08>you\n[01:33.60]Handsome, <01:34.26>you're <01:34.46>a <01:34.65>mansion <01:35.23>with <01:35.38>a <01:35.53>view\n[01:35.81]Do <01:36.00>the <01:36.20>girls <01:36.51>back <01:36.85>home <01:37.11>touch <01:37.43>you <01:37.73>like <01:38.06>I <01:38.36>do?\n[01:41.14]Long <01:41.50>night, <01:41.87>with <01:42.03>your <01:42.19>hands <01:42.47>up <01:42.80>in <01:42.98>my <01:43.15>hair\n[01:43.66]Echoes <01:44.36>of <01:44.54>your <01:44.71>footsteps <01:45.33>on <01:45.51>the <01:45.69>stairs\n[01:46.18]Stay <01:46.56>here, <01:46.89>honey, <01:47.23>I <01:47.53>don't <01:47.84>wanna <01:48.26>share\n[01:50.30]'Cause <01:50.53>I <01:50.73>like <01:51.60>you\n[01:53.32]\n[01:51.90]This <01:52.09>ain't <01:52.27>for <01:52.42>the <01:52.65>best\n[01:53.77]My <01:54.12>reputation's <01:55.12>never <01:55.42>been <01:55.77>worse, <01:56.05>so\n[01:56.94]You <01:57.12>must <01:57.29>like <01:57.61>me <01:57.94>for <01:58.26>me\n[02:00.40]Yeah, <02:00.64>I <02:00.96>want <02:01.78>you\n[02:02.17]We <02:02.39>can't <02:02.74>make\n[02:03.88]Any <02:04.23>promises <02:04.88>now, <02:05.21>can <02:05.55>we, <02:05.88>babe?\n[02:06.99]But <02:07.15>you <02:07.28>can <02:07.44>make <02:07.75>me <02:08.05>a <02:08.38>drink\n[02:08.89]\n[02:11.15]Is <02:11.32>it <02:11.55>cool <02:11.87>that <02:12.04>I <02:12.20>said <02:12.53>all <02:12.83>that?\n[02:13.74]Is <02:13.94>it <02:14.11>chill <02:14.40>that <02:14.56>you're <02:14.73>in <02:15.06>my <02:15.36>head?\n[02:16.22]'Cause <02:16.44>I <02:16.59>know <02:16.92>that <02:17.09>it's <02:17.29>deli<02:17.89>cate\n[02:21.29]Is <02:21.47>it <02:21.66>cool <02:21.99>that <02:22.17>I <02:22.35>said <02:22.64>all <02:22.96>that?\n[02:23.76]Is <02:23.99>it <02:24.19>too <02:24.49>soon <02:24.64>to <02:24.83>do <02:25.13>this <02:25.46>yet?\n[02:26.31]'Cause <02:26.49>I <02:26.69>know <02:27.04>that <02:27.18>it's <02:27.38>deli<02:27.96>cate\n[02:30.48]Isn't <02:30.80>it? <02:31.15>Isn't <02:31.45>it? <02:31.77>Isn't <02:32.05>it?\n[02:33.65]Isn't <02:33.94>it?\n[02:35.46]Isn't <02:35.83>it? <02:36.16>Isn't <02:36.48>it? <02:36.81>Isn't <02:37.10>it?\n[02:38.69]Isn't <02:38.97>it <02:39.93>deli<02:40.55>cate?\n[02:41.07]\n[02:42.09]Some<02:42.59>times <02:43.07>I <02:43.54>won<02:44.01>der <02:44.52>when <02:44.99>you <02:45.44>sleep\n[02:47.18]Are <02:47.63>you <02:48.10>e<02:48.61>ver <02:49.15>dream<02:49.63>ing <02:50.07>of <02:50.52>me?\n[02:52.20]Some<02:52.69>times <02:53.20>when <02:53.62>I <02:54.04>look <02:54.63>in<02:55.08>to <02:55.52>your <02:56.04>eyes\n[02:57.27]I <02:57.77>pre<02:58.17>tend <02:58.66>you're <02:59.09>mine, <02:59.82>all <03:00.24>the <03:00.69>damn <03:01.19>time\n[03:03.57]'Cause <03:03.77>I <03:04.03>like <03:04.82>you\n[03:06.56]\n[03:04.28]Is <03:04.43>it <03:04.61>cool <03:04.90>that <03:05.07>I <03:05.24>said <03:05.53>all <03:05.83>that?\n[03:06.73]Is <03:06.90>it <03:07.12>chill <03:07.43>that <03:07.61>you're <03:07.75>in <03:08.05>my <03:08.37>head?\n[03:09.26]'Cause <03:09.43>I <03:09.63>know <03:09.95>that <03:10.12>it's <03:10.28>deli<03:10.89>cate\n[03:13.62]Yeah, <03:13.89>I <03:14.31>want <03:15.09>you\n[03:14.37]Is <03:14.57>it <03:14.73>cool <03:15.02>that <03:15.19>I <03:15.36>said <03:15.65>all <03:15.97>that?\n[03:16.88]Is <03:17.06>it <03:17.25>too <03:17.53>soon <03:17.70>to <03:17.87>do <03:18.16>this <03:18.55>yet?\n[03:19.39]'Cause <03:19.55>I <03:19.74>know <03:20.07>that <03:20.24>it's <03:20.42>deli<03:20.99>cate\n[03:23.76]'Cause <03:23.99>I <03:24.23>like <03:25.21>you\n[03:26.55]\n[03:24.48]Is <03:24.65>it <03:24.83>cool <03:25.11>that <03:25.29>I <03:25.46>said <03:25.76>all <03:26.08>that?\n[03:26.95]Is <03:27.12>it <03:27.33>chill <03:27.65>that <03:27.82>you're <03:27.99>in <03:28.30>my <03:28.62>head?\n[03:29.46]'Cause <03:29.64>I <03:29.83>know <03:30.17>that <03:30.37>it's <03:30.52>deli<03:31.13>cate\n[03:33.90]\n[03:33.96]Yeah, <03:34.12>I <03:34.45>want <03:35.36>you\n[03:34.57]Is <03:34.75>it <03:34.91>cool <03:35.22>that <03:35.38>I <03:35.55>said <03:35.86>all <03:36.14>that?\n[03:37.09]Is <03:37.24>it <03:37.44>too <03:37.76>soon <03:37.89>to <03:38.07>do <03:38.38>this <03:38.73>yet?\n[03:39.57]'Cause <03:39.75>I <03:39.95>know <03:40.28>that <03:40.44>it's <03:40.62>deli<03:41.26>cate\n[03:43.06]Deli<03:43.73>cate\n[03:44.19]"

LINES = []

TIME_PATTERN = r"(\d+):([0-5]?\d(?:\.\d+)?)"
LINE_TAG = re.compile(r"\[" + TIME_PATTERN + r"\]")
WORD_TAG = re.compile(r"<" + TIME_PATTERN + r">")


@dataclass(frozen=True)
class LyricLine:
    start: float
    segments: Tuple[Tuple[float, str], ...]
    end: Optional[float] = None

    @property
    def text(self):
        return "".join(text for _, text in self.segments)


def seconds(match):
    return int(match[1]) * 60 + float(match[2])


def parse_lrc(text):
    """Baca LRC biasa/enhanced, metadata offset, dan tag waktu berulang."""
    raw_rows = []
    offset = 0.0
    for raw in text.splitlines():
        setting = re.fullmatch(r"\[offset:\s*([+-]?\d+)\s*\]", raw.strip(), re.I)
        if setting:
            offset = int(setting[1]) / 1000
            continue
        stamps = list(LINE_TAG.finditer(raw))
        if not stamps:
            continue
        body = raw[stamps[-1].end():].strip()
        first_start = seconds(stamps[0])
        for stamp in stamps:
            raw_rows.append((seconds(stamp), first_start, body))

    rows = []
    for start, reference, body in raw_rows:
        word_stamps = list(WORD_TAG.finditer(body))
        if not word_stamps:
            parts = [(start + offset, body)]
        else:
            parts = [(start + offset, body[:word_stamps[0].start()])]
            for index, stamp in enumerate(word_stamps):
                stop = (
                    word_stamps[index + 1].start()
                    if index + 1 < len(word_stamps) else len(body)
                )
                parts.append((
                    seconds(stamp) + start - reference + offset,
                    body[stamp.end():stop],
                ))
        rows.append(LyricLine(start + offset, tuple(parts)))
    rows.sort(key=lambda row: row.start)
    validate(rows)
    return rows


def load_lrc(path):
    return parse_lrc(Path(path).read_text(encoding="utf-8-sig"))


def load_txt(path, duration=4.0, gap=0.6):
    """TXT memakai jadwal perkiraan, bukan sinkronisasi dengan rekaman."""
    texts = [
        row.strip()
        for row in Path(path).read_text(encoding="utf-8-sig").splitlines()
        if row.strip()
    ]
    return [
        LyricLine(
            index * (duration + gap),
            ((index * (duration + gap), text),),
            index * (duration + gap) + duration,
        )
        for index, text in enumerate(texts)
    ]


def validate(lines):
    if not lines or not any(line.text.strip() for line in lines):
        raise ValueError("Belum ada lirik yang bisa ditampilkan.")
    for line in lines:
        if not math.isfinite(line.start):
            raise ValueError("Timestamp harus berupa angka yang valid.")
        previous = line.start
        for stamp, text in line.segments:
            if not math.isfinite(stamp) or stamp < previous:
                raise ValueError("Timestamp kata dalam satu baris harus berurutan.")
            if not isinstance(text, str):
                raise ValueError("Lirik harus berupa teks.")
            if any(ord(char) < 32 for char in text):
                raise ValueError("Lirik mengandung karakter kontrol terminal.")
            previous = stamp
        if line.end is not None:
            if not math.isfinite(line.end) or line.end <= previous:
                raise ValueError("Waktu selesai harus setelah timestamp terakhir.")


def build_events(lines):
    """Jadwal absolut untuk setiap huruf; baris vokal boleh bertumpuk."""
    boundaries = sorted(set(line.start for line in lines))
    events = []
    serial = 0
    for line_id, line in enumerate(lines):
        if not line.text:
            continue
        events.append((line.start, 0, serial, line_id, -1, ""))
        serial += 1
        char_position = 0
        for part_id, (start, text) in enumerate(line.segments):
            if not text:
                continue
            if part_id + 1 < len(line.segments):
                end = line.segments[part_id + 1][0]
            elif line.end is not None:
                end = line.end
            else:
                duration = (
                    4.0 if len(line.segments) == 1
                    else min(0.6, max(0.16, len(text.rstrip()) * 0.055))
                )
                next_id = bisect.bisect_right(boundaries, start)
                if next_id < len(boundaries):
                    duration = min(duration, boundaries[next_id] - start)
                end = start + duration
            interval = (end - start) / max(len(text) - 1, 1)
            for index, char in enumerate(text):
                events.append((
                    start + index * interval, 1, serial,
                    line_id, char_position, char,
                ))
                serial += 1
                char_position += 1
    return sorted(events)


def wait_until(deadline):
    while True:
        remaining = deadline - time.perf_counter()
        if remaining <= 0:
            return
        time.sleep(min(remaining, 0.02))


def supports_ansi():
    if not sys.stdout.isatty() or os.environ.get("TERM") == "dumb":
        return False
    if os.name != "nt":
        return True
    try:
        import ctypes
        kernel = ctypes.windll.kernel32
        handle = kernel.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        return bool(
            kernel.GetConsoleMode(handle, ctypes.byref(mode))
            and kernel.SetConsoleMode(handle, mode.value | 0x0004)
        )
    except (AttributeError, OSError):
        return False


class TerminalRenderer:
    """Cadangkan baris untuk setiap vokal, agar teks bertumpuk tidak tercampur."""

    def __init__(self, lines, stream=None, columns=None):
        self.lines = lines
        self.stream = stream if stream is not None else sys.stdout
        self.width = max(1, (columns or shutil.get_terminal_size((80, 24)).columns) - 1)
        self.row_starts = {}
        self.cursor_row = 0

    def start(self, line_id):
        text = self.lines[line_id].text
        height = max(1, (len(text) + self.width - 1) // self.width)
        self.row_starts[line_id] = self.cursor_row
        self.stream.write("\n" * height)
        self.cursor_row += height
        self.stream.flush()

    def put(self, line_id, position, char):
        row = self.row_starts[line_id] + position // self.width
        column = position % self.width
        distance = self.cursor_row - row
        movement = "\r" + ("\033[{}A".format(distance) if distance else "")
        if column:
            movement += "\033[{}C".format(column)
        movement += char + "\r"
        if distance:
            movement += "\033[{}B".format(distance)
        self.stream.write(movement)
        self.stream.flush()


class PlainRenderer:
    """Fallback tanpa ANSI: tahan bagian vokal berikutnya jika masih bertumpuk."""

    def __init__(self, lines, stream=None):
        self.lines = lines
        self.stream = stream if stream is not None else sys.stdout
        self.buffers = ["" for _ in lines]
        self.printed = [0 for _ in lines]
        self.current = 0

    def start(self, line_id):
        pass

    def put(self, line_id, position, char):
        self.buffers[line_id] += char
        while self.current < len(self.lines):
            current = self.current
            if not self.lines[current].text:
                self.current += 1
                continue
            self.stream.write(self.buffers[current][self.printed[current]:])
            self.printed[current] = len(self.buffers[current])
            if len(self.buffers[current]) < len(self.lines[current].text):
                break
            self.stream.write("\n")
            self.current += 1
        self.stream.flush()


def play(lines, offset=0.0, from_start=False, plain=False):
    origin = time.perf_counter()
    first_start = next(line.start for line in lines if line.text)
    base = 0.0 if from_start else first_start
    renderer = (
        PlainRenderer(lines) if plain or not supports_ansi()
        else TerminalRenderer(lines)
    )
    for stamp, _, _, line_id, position, char in build_events(lines):
        wait_until(origin + stamp - base + offset)
        if position < 0:
            renderer.start(line_id)
        else:
            renderer.put(line_id, position, char)


def main():
    parser = argparse.ArgumentParser(
        description="Delicate — Taylor Swift | efek ketik dengan lirik tertanam.",
        epilog=(
            "Audio diputar terpisah. Timestamp kata mengikuti LRC unggahan; "
            "gerakan huruf dan akhir kata terakhir memakai perkiraan."
        ),
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--lrc", help="Gunakan file LRC lain.")
    source.add_argument("--txt", help="Gunakan TXT: satu baris lirik per baris.")
    parser.add_argument("--from-start", action="store_true",
                        help="Ikuti waktu sejak detik nol LRC.")
    parser.add_argument("--preview", action="store_true",
                        help="Cetak seluruh lirik tanpa menunggu atau tag waktu.")
    parser.add_argument("--offset", type=float, default=0.0,
                        help="Geser waktu (detik): positif lebih lambat.")
    parser.add_argument("--line-duration", type=float, default=4.0,
                        help="Durasi ketik per baris TXT (default: 4).")
    parser.add_argument("--gap", type=float, default=0.6,
                        help="Jeda antarbaris TXT (default: 0.6).")
    parser.add_argument("--plain", action="store_true",
                        help="Gunakan keluaran berurutan tanpa kontrol ANSI.")
    args = parser.parse_args()
    try:
        if not math.isfinite(args.offset):
            raise ValueError("Offset harus berupa angka yang valid.")
        if args.txt:
            if not math.isfinite(args.line_duration) or args.line_duration <= 0:
                raise ValueError("--line-duration harus lebih besar dari nol.")
            if not math.isfinite(args.gap) or args.gap < 0:
                raise ValueError("--gap harus nol atau lebih.")
            lines = load_txt(args.txt, args.line_duration, args.gap)
        elif args.lrc:
            lines = load_lrc(args.lrc)
        elif LINES:
            lines = [
                LyricLine(start, ((start, text),), end)
                for start, end, text in LINES
            ]
            lines.sort(key=lambda row: row.start)
        else:
            lines = parse_lrc(EMBEDDED_LRC)
        validate(lines)
        print("=" * 34)
        print(TITLE.center(34))
        print(ARTIST.center(34))
        print("=" * 34, flush=True)
        if args.preview:
            print("\n".join(line.text for line in lines if line.text))
            return 0
        play(lines, args.offset, args.from_start, args.plain)
    except KeyboardInterrupt:
        print("\nDihentikan.")
        return 130
    except (OSError, ValueError, UnicodeError) as exc:
        print("Error: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

