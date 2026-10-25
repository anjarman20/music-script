#!/usr/bin/env python3
"""Enchanted — Taylor Swift.

Lirik dan timestamp tertanam dari LRC yang Bos unggah.
Taruh enchanted.mp3 di folder yang sama dengan script ini.

Persiapan sekali: python -m pip install pygame
Jalankan:        python enchanted_player.py
Lirik saja:      python enchanted_player.py --silent
Preview:        python enchanted_player.py --preview
Koreksi waktu:  python enchanted_player.py --offset 0.3

Audio diputar dari awal; baris pertama muncul pada detik 13.26.
Timestamp kata/suku kata mengikuti LRC. Pengetikan di antara huruf dan
akhir kata terakhir memakai perkiraan. Clock lirik mengikuti audio.
Musik tetap berjalan sampai outro selesai. Ctrl+C menghentikan keduanya.
Tag waktu kata yang mundur maksimal 0.1 detik disamakan dengan tag
sebelumnya, agar kesalahan pembulatan tidak mengubah urutan teks.

Python 3.8+. Pygame hanya diperlukan untuk audio; --silent dan --preview
bisa digunakan tanpa pygame atau file MP3.
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


TITLE = 'Enchanted'
ARTIST = 'Taylor Swift'
DEFAULT_AUDIO_NAME = 'enchanted.mp3'
EMBEDDED_LRC = '[id: bie9zb46]\n[ar: Taylor Swift]\n[al: Speak Now]\n[ti: Enchanted]\n[length: 05:52]\n\n[00:13.26]There <00:13.63>I <00:14.00>was <00:14.36>again <00:15.08>tonight\n[00:16.18]Forcing <00:16.95>laughter, <00:17.68>faking <00:18.36>smiles\n[00:19.20]Same <00:19.50>old <00:19.85>tired, <00:20.62>lonely <00:21.35>place\n[00:25.03]Walls <00:25.43>of <00:25.72>insincerity\n[00:27.93]Shifting <00:28.67>eyes <00:29.00>and <00:29.37>vacancy\n[00:30.86]Vanished <00:31.61>when <00:31.94>I <00:32.32>saw <00:32.69>your <00:33.06>face\n[00:34.11]\n[00:34.24]All <00:34.52>I <00:34.85>can <00:35.19>say <00:35.52>is, <00:35.90>"It <00:36.67>was <00:37.84>enchanting <00:38.89>to <00:39.26>meet <00:39.96>you"\n[00:45.26]\n[00:48.44]Your <00:48.76>eyes <00:49.13>whispered, <00:49.09>"Have <00:50.26>we <00:50.63>met?"\n[00:51.35]Across <00:51.68>the <00:52.06>room, <00:52.45>your <00:52.79>silhouette\n[00:54.29]Starts <00:54.61>to <00:55.01>make <00:55.36>its <00:55.74>way <00:56.11>to <00:56.48>me\n[00:59.98]The <01:00.14>playful <01:00.83>conversation <01:02.29>starts\n[01:03.07]Counter <01:03.79>all <01:04.16>your <01:04.50>quick <01:04.81>remarks\n[01:05.64]Like <01:06.32>passing <01:06.76>notes <01:07.09>in <01:07.42>secrecy\n[01:09.76]\n[01:10.87]And <01:11.14>it <01:11.87>was <01:12.95>enchanting <01:14.05>to <01:14.44>meet <01:15.12>you\n[01:20.95]All <01:21.32>I <01:21.66>can <01:22.05>say <01:22.38>is <01:22.75>I <01:23.52>was <01:24.63>enchanted <01:25.75>to <01:26.12>meet <01:26.80>you\n[01:32.55]\n[01:36.00]This <01:36.65>night <01:37.44>is <01:38.14>sparkling, <01:39.69>don\'t <01:39.99>you <01:40.35>let <01:40.72>it <01:41.12>go\n[01:41.92]I\'m <01:42.59>wonder<01:43.90>struck, <01:44.81>blushing <01:45.54>all <01:45.86>the <01:46.22>way <01:46.63>home\n[01:47.71]I\'ll <01:48.37>spend <01:49.14>for<01:49.91>ever <01:51.40>wondering <01:52.15>if <01:52.47>you <01:52.82>knew\n[01:53.21]I <01:53.50>was <01:53.90>enchanted <01:55.05>to <01:55.40>meet <01:56.12>you\n[02:01.45]\n[02:04.41]The <02:04.57>lingering <02:05.28>question <02:06.03>kept <02:06.36>me <02:06.73>up\n[02:07.47]2 <02:07.79>AM, <02:08.60>who <02:08.96>do <02:09.31>you <02:09.65>love?\n[02:10.29]I <02:10.81>wonder <02:11.12>till <02:11.46>I\'m <02:11.82>wide <02:12.26>awake\n[02:16.13]And <02:16.28>now <02:16.60>I\'m <02:16.95>pacing <02:17.70>back <02:18.03>and <02:18.41>forth\n[02:19.15]Wishing <02:19.92>you <02:20.25>were <02:20.62>at <02:20.97>my <02:21.36>door\n[02:21.94]I\'d <02:22.52>open <02:22.82>up <02:23.17>and <02:23.56>you <02:23.92>would <02:24.29>say\n[02:25.81]\n[02:26.50]"Hey, <02:27.29>it <02:27.98>was <02:29.08>enchanting <02:30.20>to <02:30.50>meet <02:31.23>you"\n[02:37.48]All <02:37.83>I <02:38.17>know <02:38.50>is <02:38.88>I <02:39.63>was <02:40.78>enchanted <02:41.88>to <02:42.23>meet <02:42.95>you\n[02:50.23]\n[02:52.10]This <02:52.83>night <02:53.52>is <02:54.25>sparkling, <02:55.77>don\'t <02:56.10>you <02:56.48>let <02:56.87>it <02:57.25>go\n[02:58.03]I\'m <02:58.64>wonder<03:00.11>struck, <03:00.94>blushing <03:01.66>all <03:01.99>the <03:02.36>way <03:02.75>home\n[03:03.80]I\'ll <03:04.47>spend <03:05.24>for<03:05.97>ever <03:07.52>wondering <03:08.24>if <03:08.56>you <03:08.90>knew\n[03:15.56]This <03:16.19>night <03:17.01>is <03:17.71>flaw<03:18.44>less, <03:19.24>don\'t <03:19.54>you <03:19.91>let <03:20.28>it <03:20.64>go\n[03:21.41]I\'m <03:22.07>wonder<03:23.53>struck, <03:24.34>dancing <03:25.01>around <03:25.43>all <03:25.81>alone\n[03:27.28]I\'ll <03:27.91>spend <03:28.64>for<03:29.43>ever <03:30.94>wondering <03:31.64>if <03:31.99>you <03:32.33>knew\n[03:32.75]I <03:33.08>was <03:33.45>enchanted <03:34.56>to <03:34.95>meet <03:35.66>you\n[03:40.75]\n[03:58.82]This <03:59.09>is <03:59.44>me <04:00.15>praying <04:00.87>that\n[04:02.01]This <04:02.38>was <04:02.74>the <04:03.11>very <04:03.81>first <04:04.19>page\n[04:04.99]Not <04:05.32>where <04:05.65>the <04:06.02>storyline <04:07.15>ends\n[04:07.94]My <04:08.25>thoughts <04:08.59>will <04:08.94>echo <04:09.69>your <04:10.04>name\n[04:10.80]Until <04:11.55>I <04:11.90>see <04:12.23>you <04:12.62>again\n[04:13.75]These <04:14.10>are <04:14.45>the <04:14.83>words <04:15.18>I <04:15.55>held <04:15.93>back\n[04:16.66]As <04:17.02>I <04:17.36>was <04:17.72>leaving <04:18.47>too <04:18.84>soon\n[04:19.58]I <04:19.93>was <04:20.26>enchanted <04:21.45>to <04:21.81>meet <04:22.53>you\n[04:27.51]\n[04:25.10]Please <04:25.83>don\'t <04:26.58>be <04:26.92>in <04:27.30>love <04:27.68>with <04:28.03>some<04:28.78>one <04:29.50>else\n[04:30.96]Please <04:31.68>don\'t <04:32.44>have <04:32.78>somebody <04:33.86>waiting <04:34.60>on <04:35.35>you\n[04:36.80]Please <04:37.53>don\'t <04:38.26>be <04:38.63>in <04:38.97>love <04:39.32>with <04:39.68>some<04:40.47>one <04:41.20>else\n[04:42.69]Please <04:43.35>don\'t <04:44.14>have <04:44.44>somebody <04:45.57>waiting <04:46.32>on <04:46.99>you\n[04:47.82]\n[04:49.24]This <04:49.93>night <04:50.71>is <04:51.38>sparkling, <04:52.90>don\'t <04:53.21>you <04:53.60>let <04:53.98>it <04:54.33>go\n[04:55.11]I\'m <04:55.79>wonder<04:57.13>struck, <04:58.04>blushing <04:58.78>all <04:59.11>the <04:59.48>way <04:59.85>home\n[05:00.93]I\'ll <05:01.53>spend <05:02.35>for<05:03.10>ever <05:04.64>wondering <05:05.40>if <05:05.72>you <05:06.07>knew\n[05:09.85]\n[05:12.69]This <05:13.27>night <05:14.09>is <05:14.77>flaw<05:15.56>less, <05:16.34>don\'t <05:16.66>you <05:17.02>let <05:17.39>it <05:17.74>go\n[05:18.50]I\'m <05:19.19>wonder<05:20.62>struck, <05:21.44>dancing <05:22.19>around <05:22.54>all <05:22.89>alone\n[05:24.36]I\'ll <05:25.06>spend <05:25.81>for<05:26.53>ever <05:28.06>wondering <05:28.74>if <05:29.09>you <05:29.46>knew\n[05:29.85]I <05:30.17>was <05:30.52>enchanted <05:31.65>to <05:32.05>meet <05:32.77>you\n[05:38.04]\n[05:35.46]Please <05:36.09>don\'t <05:36.84>be <05:37.22>in <05:37.55>love <05:37.91>with <05:38.24>some<05:39.00>one <05:39.79>else\n[05:41.20]Please <05:41.92>don\'t <05:42.70>have <05:42.99>somebody <05:44.14>waiting <05:44.89>on <05:45.63>you\n[05:46.86]'

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
        normalized = []
        previous = start + offset
        for stamp, text in parts:
            if stamp < previous:
                if previous - stamp > 0.1 + 1e-9:
                    raise ValueError(
                        "Timestamp kata mundur lebih dari 0.1 detik. "
                        "Periksa LRC pada detik {:.2f}.".format(start)
                    )
                stamp = previous
            normalized.append((stamp, text))
            previous = stamp
        rows.append(LyricLine(start + offset, tuple(normalized)))
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

