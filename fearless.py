"""Fearless — Taylor Swift
    python fearless.py
    python fearless.py --from-start
    python fearless.py --preview
    python fearless.py --offset 0.3
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


TITLE = "Fearless"
ARTIST = "Taylor Swift"

EMBEDDED_LRC = "[id: ngidjnnq]\n[ar: Taylor Swift]\n[al: Fearless]\n[ti: Fearless]\n[length: 04:01]\n\n[00:21.03]There's <00:21.34>somethin' <00:21.92>'bout <00:22.19>the <00:22.54>way\n[00:23.38]The <00:23.75>street <00:24.07>looks <00:24.37>when <00:24.63>it's <00:24.95>just <00:25.55>rained\n[00:26.14]There's <00:26.43>a <00:26.77>glow <00:27.37>off <00:27.63>the <00:27.95>pavement\n[00:28.85]You <00:29.18>walk <00:29.47>me <00:29.80>to <00:30.08>the <00:30.38>car\n[00:30.93]And <00:31.25>you <00:31.56>know <00:31.91>I <00:32.21>wanna <00:32.78>ask <00:33.05>you <00:33.41>to <00:33.68>dance <00:34.25>right <00:34.86>there\n[00:35.71]In <00:36.04>the <00:36.34>middle <00:36.96>of <00:37.26>the <00:37.54>parking <00:38.16>lot, <00:39.33>yeah\n[00:43.81]Oh, <00:44.37>yeah\n[00:46.44]\n[00:49.83]We're <00:50.19>drivin' <00:50.74>down <00:51.04>the <00:51.34>road\n[00:52.21]I <00:52.56>wonder <00:53.13>if <00:53.45>you <00:54.05>know\n[00:54.65]I'm <00:54.98>tryin' <00:55.57>so <00:56.15>hard <00:56.67>not <00:57.00>to <00:57.33>get <00:57.63>caught <00:57.96>up <00:58.55>now\n[00:59.46]But <00:59.76>you're <01:00.06>just <01:00.36>so <01:00.95>cool\n[01:01.51]Run <01:01.81>your <01:02.16>hands <01:02.71>through <01:03.08>your <01:03.63>hair\n[01:04.47]Absent-<01:05.09>mindedly <01:06.27>makin' <01:06.91>me <01:07.52>want <01:08.11>you\n[01:08.77]\n[01:09.01]And <01:09.35>I <01:09.63>don't <01:09.95>know <01:10.55>how <01:11.15>it <01:11.73>gets <01:12.35>better <01:12.95>than <01:13.51>this\n[01:13.86]You <01:14.16>take <01:14.44>my <01:14.76>hand <01:15.07>and <01:15.39>drag <01:15.67>me <01:15.94>head <01:16.54>first\n[01:17.07]Fearless\n[01:18.64]And <01:18.94>I <01:19.22>don't <01:19.54>know <01:20.10>why <01:20.80>but <01:21.30>with <01:21.94>you\n[01:22.40]I'd <01:22.87>dance <01:23.78>in <01:24.04>a <01:24.34>storm <01:24.94>in <01:25.26>my <01:25.56>best <01:26.14>dress\n[01:26.69]Fearless\n[01:28.05]\n[01:37.73]So <01:38.11>baby, <01:38.75>drive <01:39.30>slow\n[01:40.46]Till <01:40.83>we <01:41.13>run <01:41.41>out <01:41.75>of <01:42.03>road <01:42.90>in <01:43.20>this <01:43.55>one-<01:43.86>horse <01:44.45>town\n[01:45.20]I <01:45.30>wanna <01:45.92>stay <01:46.25>right <01:46.82>here <01:47.69>in <01:47.99>this <01:48.34>passenger's <01:49.29>seat\n[01:49.79]You <01:50.12>put <01:50.44>your <01:50.75>eyes <01:51.22>on <01:51.64>me\n[01:52.45]In <01:52.84>this <01:53.14>moment <01:53.74>now, <01:54.27>capture <01:54.94>it, <01:55.18>remember <01:56.12>it\n[01:56.68]\n[01:57.00]'Cause <01:57.33>I <01:57.63>don't <01:57.95>know <01:58.55>how <01:59.16>it <01:59.75>gets <02:00.33>better <02:00.92>than <02:01.48>this\n[02:01.89]You <02:02.19>take <02:02.47>my <02:02.79>hand <02:03.10>and <02:03.42>drag <02:03.70>me <02:03.97>head <02:04.57>first\n[02:05.12]Fearless\n[02:06.68]And <02:06.98>I <02:07.27>don't <02:07.58>know <02:08.15>why <02:08.85>but <02:09.35>with <02:09.98>you\n[02:10.32]I'd <02:10.97>dance <02:11.72>in <02:12.02>a <02:12.33>storm <02:12.93>in <02:13.23>my <02:13.55>best <02:14.13>dress\n[02:14.52]Fearless\n[02:15.93]\n[02:20.10]Oh-<02:20.45>oh\n[02:21.17]\n[02:35.38]Well, <02:35.71>you <02:36.01>stood <02:36.68>there <02:36.98>with <02:37.28>me <02:37.81>in <02:38.16>the <02:38.44>doorway\n[02:39.36]My <02:39.73>hands <02:40.30>shake\n[02:40.52]I'm <02:40.89>not <02:41.41>usually <02:42.56>this <02:43.19>way <02:44.12>but\n[02:44.99]You <02:45.30>pull <02:45.64>me <02:45.94>in <02:46.22>and <02:46.54>I'm <02:46.82>a <02:47.12>little <02:47.55>more <02:47.98>brave\n[02:48.59]It's <02:48.89>the <02:49.23>first <02:49.86>kiss, <02:50.24>it's <02:50.53>flawless\n[02:51.36]Really <02:51.74>something, <02:55.18>it's <02:55.53>fearless\n[03:00.94]Oh, <03:03.67>yeah\n[03:04.72]\n[03:06.62]'Cause' <03:06.97>I <03:07.26>don't <03:07.56>know <03:08.12>how <03:08.79>it <03:09.39>gets <03:09.99>better <03:10.56>than <03:11.02>this\n[03:11.48]You <03:11.72>take <03:12.04>my <03:12.39>hand <03:12.69>and <03:13.01>drag <03:13.29>me <03:13.57>head <03:14.13>first\n[03:14.67]Fearless\n[03:16.16]And <03:16.54>I <03:16.84>don't <03:17.14>know <03:17.72>why <03:18.32>but <03:18.90>with <03:19.52>you\n[03:19.83]I'd <03:20.43>dance <03:21.21>in <03:21.58>a <03:21.98>storm <03:22.52>in <03:22.83>my <03:23.15>best <03:23.73>dress\n[03:24.32]Fearless\n[03:25.58]\n[03:25.78]'Cause <03:26.11>I <03:26.41>don't <03:26.74>know <03:27.31>how <03:27.88>it <03:28.49>gets <03:29.14>better <03:29.74>than <03:30.31>this\n[03:30.69]You <03:30.97>take <03:31.24>my <03:31.56>hand <03:31.90>and <03:32.16>drag <03:32.47>me <03:32.76>head <03:33.36>first\n[03:33.90]Fearless\n[03:35.40]And <03:35.70>I <03:35.99>don't <03:36.30>know <03:36.92>why <03:37.45>but <03:38.12>with <03:38.73>you\n[03:39.09]I'd <03:39.59>dance <03:40.49>in <03:40.80>a <03:41.14>storm <03:41.70>in <03:41.99>my <03:42.32>best <03:42.89>dress\n[03:43.40]Fearless\n[03:45.29]\n[03:46.39]Oh-<03:46.92>oh\n[03:48.92]Oh, <03:49.53>yeah\n[03:49.83]"

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
        description="Fearless — Taylor Swift | efek ketik dengan lirik tertanam.",
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

