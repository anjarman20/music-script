"""Stand By Me — Oasis.

Taruh stand-by-me.mp3 di folder yang sama dengan script ini.
Pasang sekali: python -m pip install pygame
Jalankan:     python stand_by_me_player.py
Lirik saja:   python stand_by_me_player.py --silent
Preview:      python stand_by_me_player.py --preview
Geser waktu:  python stand_by_me_player.py --offset 0.3
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


TITLE = 'Stand By Me'
ARTIST = 'Oasis'
DEFAULT_AUDIO_NAME = 'stand-by-me.mp3'


EMBEDDED_LRC = "[id: bwu8tbeg]\n[ar: Oasis]\n[al: Be Here Now]\n[ti: Stand By Me]\n[length: 05:56]\n\n[00:31.31]Made <00:31.80>a <00:31.95>meal <00:32.45>and <00:32.71>threw <00:33.20>it <00:33.40>up <00:33.88>on <00:34.52>Sun<00:35.27>day\n[00:35.97]I've <00:37.04>got a <00:37.72>lot of <00:38.21>things <00:38.62>to <00:38.79>learn\n[00:42.55]Said <00:43.05>I <00:43.03>would <00:43.76>and <00:44.05>I'll <00:44.45>be <00:44.79>leaving <00:45.84>one <00:46.46>day\n[00:47.27]Be<00:47.52>fore <00:47.97>my <00:48.27>heart <00:48.90>starts <00:49.64>to <00:50.04>burn\n[00:51.04]\n[00:53.66]So <00:53.94>what's <00:54.27>the <00:54.45>matter <00:55.34>with <00:55.71>you?\n[00:59.46]Sing <00:59.91>me <01:00.25>something <01:01.31>new\n[01:03.15]Don't <01:03.45>you <01:03.68>know\n[01:04.21]The <01:04.37>cold <01:04.90>and <01:05.16>wind <01:05.60>and <01:05.85>rain <01:06.30>don't <01:06.64>know\n[01:07.13]They <01:07.34>only <01:07.89>seem <01:08.53>to <01:08.69>come and <01:09.22>go <01:09.78>aw<01:09.95>ay\n[01:14.60]\n[01:16.42]Times <01:16.90>are <01:17.07>hard <01:17.54>when <01:17.88>things <01:18.29>have <01:18.55>got <01:18.95>no <01:19.68>meaning\n[01:21.12]I've <01:22.46>found a <01:22.80>key <01:23.17>upon <01:23.70>the <01:23.87>floor\n[01:27.73]Maybe <01:28.39>you <01:28.83>and <01:29.14>I <01:29.49>will <01:29.85>not <01:30.24>believe <01:31.57>in\n[01:32.34]The <01:32.64>things <01:33.09>we <01:33.37>find <01:33.76>behind <01:34.80>the <01:35.09>door\n[01:36.12]\n[01:38.81]So <01:39.05>what's <01:39.39>the <01:39.55>matter <01:40.38>with <01:40.81>you?\n[01:44.60]Sing <01:45.00>me <01:45.28>something <01:46.37>new\n[01:48.19]Don't <01:48.53>you <01:48.70>know\n[01:49.33]The <01:49.50>cold <01:49.98>and <01:50.25>wind <01:50.69>and <01:51.00>rain <01:51.40>don't <01:51.75>know\n[01:52.24]They <01:52.51>only <01:53.01>seem <01:53.62>to come <01:54.13>and go <01:54.83>aw<01:55.06>ay\n[01:59.54]\n[02:01.99]Stand <02:02.53>by <02:03.31>me\n[02:04.94]Nobody <02:06.11>knows <02:07.74>the <02:07.89>way <02:08.23>it's <02:08.44>gonna <02:08.96>be\n[02:12.55]Stand <02:13.23>by <02:13.85>me\n[02:15.45]Nobody <02:16.67>knows <02:18.25>the <02:18.46>way <02:18.79>it's <02:19.00>gonna <02:19.56>be\n[02:23.20]Stand <02:23.79>by <02:24.53>me\n[02:26.06]Nobody <02:27.23>knows <02:28.91>the <02:29.13>way <02:29.41>it's <02:29.63>gonna <02:30.18>be\n[02:33.78]Stand <02:34.40>by <02:35.08>me\n[02:36.61]Nobody <02:37.83>knows\n[02:41.59]Yeah, <02:42.43>nobody <02:43.52>knows\n[02:47.98]The <02:48.15>way <02:48.43>it's <02:48.70>gonna <02:49.24>be\n[02:50.17]\n[02:55.90]If <02:56.21>you're <02:56.48>leaving, <02:57.18>will <02:57.59>you <02:57.94>take <02:58.44>me <02:59.02>with <02:59.74>you?\n[03:00.42]I'm <03:00.73>tired <03:01.13>of <03:01.45>talking <03:02.15>on <03:02.55>my <03:03.17>phone\n[03:07.13]There <03:07.50>is <03:07.85>one <03:08.25>thing <03:08.62>I <03:08.87>can <03:09.30>never <03:10.36>give <03:11.00>you\n[03:11.68]My <03:12.03>heart <03:12.50>will <03:12.83>never <03:13.51>be <03:13.83>your <03:14.50>home\n[03:15.60]\n[03:18.22]So <03:18.49>what's <03:18.87>the <03:19.08>matter <03:19.85>with <03:20.23>you?\n[03:23.90]Sing <03:24.41>me <03:24.71>something <03:25.81>new\n[03:27.63]Don't <03:28.02>you <03:28.20>know\n[03:28.75]The <03:28.89>cold <03:29.41>and <03:29.70>wind <03:30.16>and <03:30.38>rain <03:30.90>don't <03:31.21>know\n[03:31.77]They <03:31.91>only <03:32.46>seem <03:33.05>to come <03:33.59>and go <03:34.22>aw<03:34.45>ay\n[03:39.09]Hey, <03:39.85>hey\n[03:41.15]\n[03:41.45]Stand <03:42.07>by <03:42.78>me\n[03:44.39]Nobody <03:45.54>knows <03:47.15>the way <03:47.70>it's <03:47.88>gonna <03:48.39>be\n[03:52.00]Stand <03:52.75>by <03:53.33>me\n[03:54.94]Nobody <03:56.16>knows <03:57.71>the way <03:58.19>it's <03:58.49>gonna <03:59.06>be\n[04:02.60]Stand <04:03.20>by <04:03.91>me\n[04:05.66]Nobody <04:06.73>knows <04:08.33>the way <04:08.78>it's <04:09.06>gonna <04:09.58>be\n[04:13.18]Stand <04:13.85>by <04:14.51>me\n[04:16.18]Nobody <04:17.27>knows\n[04:21.11]Yeah, <04:21.78>nobody <04:22.92>knows\n[04:27.41]The way <04:27.76>it's <04:27.99>gonna <04:28.66>be\n[04:29.53]\n[04:33.09]The way <04:33.45>it's <04:33.72>gonna <04:34.28>be, <04:35.13>yeah\n[04:38.71]Maybe <04:39.32>I <04:39.64>can <04:40.01>see, <04:40.80>yeah\n[04:44.49]Don't <04:44.87>you <04:45.08>know\n[04:45.53]The <04:45.73>cold <04:46.32>and <04:46.54>wind <04:46.88>and <04:47.18>rain <04:47.65>don't <04:48.03>know\n[04:48.51]They <04:48.76>only <04:49.28>seem <04:49.92>to come <04:50.42>and <04:50.70>go <04:51.13>aw<04:51.31>ay\n[04:55.90]Hey, <04:56.80>hey!\n[04:58.14]\n[04:58.44]Stand <04:58.96>by <04:59.62>me\n[05:01.35]Nobody <05:02.42>knows <05:03.93>the way <05:04.48>it's <05:04.78>gonna <05:05.36>be\n[05:08.91]Stand <05:09.54>by <05:10.19>me\n[05:11.85]Nobody <05:12.95>knows <05:14.64>the way <05:15.09>it's <05:15.40>gonna <05:15.92>be\n[05:19.64]Stand <05:20.13>by <05:20.80>me\n[05:22.57]Nobody <05:23.61>knows <05:25.30>the way <05:25.71>it's <05:25.94>gonna <05:26.48>be\n[05:30.11]Stand <05:30.70>by <05:31.41>me\n[05:33.10]Nobody <05:34.16>knows\n[05:38.05]Yeah, <05:38.68>God <05:39.18>only <05:39.84>knows\n[05:44.25]The way <05:44.67>it's <05:44.99>gonna <05:45.58>be\n[05:46.72]"



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
    pass


class AudioPlayer:

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

