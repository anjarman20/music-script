#!/usr/bin/env python3
"""Treat You Better — Shawn Mendes.
Taruh treat-you-better.mp3 di folder yang sama dengan script ini.

Persiapan sekali: python -m pip install pygame
Jalankan:        python treat_you_better_player.py
Lirik saja:      python treat_you_better_player.py --silent
Preview:        python treat_you_better_player.py --preview
Koreksi waktu:  python treat_you_better_player.py --offset 0.3
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


TITLE = 'Treat You Better'
ARTIST = 'Shawn Mendes'
DEFAULT_AUDIO_NAME = 'treat-you-better.mp3'
EMBEDDED_LRC = "[id: ngido66j]\n[ar: Shawn Mendes]\n[al: Illuminate]\n[ti: Treat You Better]\n[length: 03:07]\n\n[00:11.74]I <00:12.94>won't <00:13.30>lie <00:14.33>to <00:14.65>you\n[00:16.71]I <00:17.03>know <00:17.33>he's <00:17.65>just <00:18.68>not <00:19.02>right <00:20.00>for <00:20.30>you\n[00:22.77]And <00:23.08>you <00:23.24>can <00:23.40>tell <00:23.64>me <00:23.81>if <00:23.99>I'm <00:24.17>off, <00:24.34>but <00:24.49>I <00:24.62>see <00:24.96>it <00:25.11>on <00:25.28>your <00:25.43>face\n[00:25.92]When <00:26.05>you <00:26.15>say <00:26.40>that <00:26.59>he's <00:26.78>the <00:27.00>one <00:27.15>that <00:27.37>you <00:27.55>want\n[00:28.76]And <00:28.95>you're <00:29.05>spending <00:29.57>all <00:29.73>your <00:29.83>time <00:30.22>in <00:30.43>this <00:30.65>wrong <00:30.88>situation\n[00:31.94]And <00:32.04>anytime <00:32.54>you <00:32.72>want <00:32.88>it <00:33.04>to <00:33.14>stop\n[00:33.63]\n[00:34.20]I <00:34.32>know <00:34.54>I <00:34.73>can <00:34.87>treat <00:35.70>you <00:36.39>better <00:38.23>than <00:38.65>he <00:39.00>can\n[00:39.78]And <00:39.94>any <00:40.26>girl <00:40.45>like <00:40.71>you <00:41.40>deserves <00:42.92>a <00:43.97>gentleman\n[00:45.53]Tell <00:45.80>me <00:45.97>why <00:46.20>are <00:46.38>we <00:46.57>wasting <00:47.10>time <00:47.51>on <00:47.68>all <00:47.85>your <00:48.05>wasted <00:48.39>crying\n[00:48.90]When <00:49.00>you <00:49.10>should <00:49.34>be <00:49.62>with <00:49.91>me <00:50.26>instead?\n[00:51.48]I <00:51.66>know <00:51.88>I <00:52.05>can <00:52.22>treat <00:52.88>you <00:53.65>better\n[00:56.54]Better <00:57.10>than <00:57.41>he <00:57.70>can\n[00:58.02]\n[00:58.12]I'll <00:58.95>stop <00:59.43>time <01:00.53>for <01:00.84>you\n[01:02.89]The <01:03.12>second <01:03.57>you <01:03.86>say <01:04.71>you'd <01:05.09>like <01:06.21>me <01:06.47>to\n[01:09.58]I <01:09.81>just <01:10.01>wanna <01:10.39>give <01:10.79>you <01:10.93>the <01:11.13>loving <01:11.49>that <01:11.70>you're <01:11.91>missing\n[01:12.49]Baby, <01:12.79>just <01:12.98>to <01:13.20>wake <01:13.47>up <01:13.71>with <01:13.93>you\n[01:15.04]Would <01:15.21>be <01:15.40>everything <01:15.95>I <01:16.07>need, <01:16.52>and <01:16.72>this <01:17.04>could <01:17.22>be <01:17.34>so <01:17.65>different\n[01:18.30]Tell <01:18.51>me <01:18.70>what <01:18.92>you <01:19.09>want <01:19.46>to <01:19.67>do\n[01:20.28]\n[01:20.30]'Cause <01:20.49>I <01:20.60>know <01:20.79>I <01:20.98>can <01:21.14>treat <01:21.95>you <01:22.64>better <01:24.45>than <01:24.86>he <01:25.21>can\n[01:26.00]And <01:26.36>any <01:26.67>girl <01:26.85>like <01:27.13>you <01:27.82>deserves <01:29.14>a <01:30.19>gentleman\n[01:31.74]Tell <01:32.02>me <01:32.19>why <01:32.41>are <01:32.59>we <01:32.78>wasting <01:33.32>time <01:33.72>on <01:33.90>all <01:34.07>your <01:34.26>wasted <01:34.61>crying\n[01:35.10]When <01:35.36>you <01:35.46>should <01:35.75>be <01:36.03>with <01:36.32>me <01:36.64>instead?\n[01:37.81]I <01:37.91>know <01:38.13>I <01:38.32>can <01:38.46>treat <01:39.28>you <01:39.99>better\n[01:42.80]Better <01:43.52>than <01:43.82>he <01:44.10>can\n[01:48.56]Better <01:49.23>than <01:49.56>he <01:49.83>can\n[01:50.39]\n[01:55.84]Give <01:56.94>me <01:57.23>a <01:57.34>sign, <01:58.18>take <01:58.70>my <01:59.01>hand, <01:59.84>we'll <02:00.12>be <02:00.30>fine\n[02:01.64]Promise <02:02.93>I <02:03.17>won't <02:04.06>let <02:04.35>you <02:04.59>down\n[02:07.04]Just <02:07.41>know <02:08.31>that <02:08.56>you <02:08.83>don't <02:09.69>have <02:09.95>to <02:10.23>do <02:11.13>this <02:11.46>alone\n[02:13.17]Promise <02:14.40>I'll <02:14.62>never <02:15.33>let <02:15.67>you <02:15.96>down\n[02:16.85]\n[02:18.09]'Cause <02:18.26>I <02:18.40>know <02:18.61>I <02:18.78>can <02:18.96>treat <02:19.80>you <02:20.48>better <02:22.22>than <02:22.60>he <02:22.92>can\n[02:23.84]And <02:24.10>any <02:24.43>girl <02:24.62>like <02:24.83>you <02:25.47>deserves <02:26.98>a <02:27.93>gentleman\n[02:29.52]Tell <02:29.88>me <02:30.06>why <02:30.28>are <02:30.44>we <02:30.66>wasting <02:31.19>time <02:31.60>on <02:31.79>all <02:31.95>your <02:32.16>wasted <02:32.59>crying\n[02:33.00]When <02:33.10>you <02:33.20>should <02:33.44>be <02:33.71>with <02:34.00>me <02:34.35>instead?\n[02:35.58]I <02:35.77>know <02:36.00>I <02:36.19>can <02:36.33>treat <02:37.14>you <02:37.85>better\n[02:40.64]Better <02:41.18>than <02:41.49>he <02:41.71>can, <02:44.73>oh\n[02:46.43]Better <02:47.11>than <02:47.44>he <02:47.71>can\n[02:52.23]Better <02:52.83>than <02:53.16>he <02:53.44>can\n[02:53.94]"

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



class AudioEnded(RuntimeError):
    """Audio selesai sebelum timestamp lirik berikutnya."""


class AudioPlayer:
    """Audio streaming; gunakan posisi mixer sebagai jam untuk lirik."""

    def __init__(self, path, volume=0.8):
        self.path = Path(path)
        self.volume = volume
        self.pygame = None

    def __enter__(self):
        if not self.path.is_file():
            raise FileNotFoundError(
                "MP3 tidak ditemukan: {}. Letakkan {} di folder script, "
                "atau tentukan --audio PATH.".format(self.path, DEFAULT_AUDIO_NAME)
            )
        os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
        try:
            import pygame
        except ImportError as exc:
            raise RuntimeError(
                "Pygame belum tersedia. Pasang dengan: python -m pip install pygame"
            ) from exc
        self.pygame = pygame
        try:
            pygame.mixer.init(buffer=512)
            pygame.mixer.music.load(str(self.path))
            pygame.mixer.music.set_volume(self.volume)
        except pygame.error as exc:
            self.close()
            raise RuntimeError(
                "Audio gagal dibuka. Periksa file dan perangkat audio: " + str(exc)
            ) from exc
        except BaseException:
            self.close()
            raise
        return self

    def start(self):
        self.pygame.mixer.music.play()

    def wait_until(self, target):
        while True:
            music = self.pygame.mixer.music
            position = music.get_pos() / 1000.0
            if position >= target:
                return
            if not music.get_busy():
                raise AudioEnded(
                    "Audio selesai sebelum semua lirik ditampilkan. "
                    "Pastikan MP3 sesuai dengan versi dan timestamp LRC."
                )
            time.sleep(min(max(target - position, 0.001), 0.01))

    def wait_finished(self):
        while self.pygame.mixer.music.get_busy():
            time.sleep(0.02)

    def close(self):
        if self.pygame is not None and self.pygame.mixer.get_init():
            try:
                self.pygame.mixer.music.stop()
                self.pygame.mixer.music.unload()
            finally:
                self.pygame.mixer.quit()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False



def play(lines, offset=0.0, from_start=False, plain=False, audio=None):
    events = build_events(lines)
    first_start = next(line.start for line in lines if line.text)
    base = 0.0 if audio is not None or from_start else first_start
    renderer = (
        PlainRenderer(lines) if plain or not supports_ansi()
        else TerminalRenderer(lines)
    )
    if audio is not None:
        audio.start()
    origin = time.perf_counter()
    for stamp, _, _, line_id, position, char in events:
        target = stamp - base + offset
        if audio is not None:
            audio.wait_until(target)
        else:
            wait_until(origin + target)
        if position < 0:
            renderer.start(line_id)
        else:
            renderer.put(line_id, position, char)
    if audio is not None:
        audio.wait_finished()



def main():
    parser = argparse.ArgumentParser(
        description=TITLE + " — " + ARTIST + " | lirik dan pemutar MP3.",
        epilog=(
            "Default: putar " + DEFAULT_AUDIO_NAME + " dari folder script. "
            "Timestamp mulai baris mengikuti LRC; kecepatan ketik huruf "
            "merupakan perkiraan. Ctrl+C menghentikan audio dan lirik."
        ),
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--lrc", help="Gunakan file LRC lain.")
    source.add_argument("--txt", help="Gunakan TXT: satu baris lirik per baris.")
    parser.add_argument("--audio", help="Path audio lain (default: MP3 di folder script).")
    parser.add_argument("--silent", "--no-audio", action="store_true",
                        help="Hanya tampilkan lirik, tanpa pygame atau MP3.")
    parser.add_argument("--from-start", action="store_true",
                        help="Mode --silent: pertahankan intro; audio selalu dari awal.")
    parser.add_argument("--preview", action="store_true",
                        help="Cetak semua lirik tanpa menunggu atau memutar audio.")
    parser.add_argument("--offset", type=float, default=0.0,
                        help="Geser lirik (detik): positif lebih lambat, negatif lebih cepat.")
    parser.add_argument("--volume", type=float, default=0.8,
                        help="Volume audio 0 sampai 1 (default: 0.8).")
    parser.add_argument("--line-duration", type=float, default=4.0,
                        help="Durasi ketik per baris TXT (default: 4).")
    parser.add_argument("--gap", type=float, default=0.6,
                        help="Jeda antarbaris TXT (default: 0.6).")
    parser.add_argument("--plain", action="store_true",
                        help="Keluaran berurutan tanpa kontrol ANSI.")
    args = parser.parse_args()
    try:
        if not math.isfinite(args.offset):
            raise ValueError("Offset harus berupa angka yang valid.")
        if not math.isfinite(args.volume) or not 0.0 <= args.volume <= 1.0:
            raise ValueError("--volume harus antara 0 dan 1.")
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
        width = max(34, len(TITLE) + 4)
        print("=" * width)
        print(TITLE.center(width))
        print(ARTIST.center(width))
        print("=" * width, flush=True)
        if args.preview:
            print("\n".join(line.text for line in lines if line.text))
            return 0
        if args.silent:
            play(lines, args.offset, args.from_start, args.plain)
        else:
            audio_path = (
                Path(args.audio).expanduser() if args.audio
                else Path(__file__).resolve().parent / DEFAULT_AUDIO_NAME
            )
            print("Audio: " + audio_path.name)
            print("Ctrl+C untuk berhenti.\n", flush=True)
            with AudioPlayer(audio_path, args.volume) as audio:
                play(lines, args.offset, plain=args.plain, audio=audio)
        return 0
    except KeyboardInterrupt:
        print("\nDihentikan.")
        return 130
    except (OSError, ValueError, UnicodeError, RuntimeError) as exc:
        print("Error: " + str(exc), file=sys.stderr)
        return 1



if __name__ == "__main__":
    raise SystemExit(main())

