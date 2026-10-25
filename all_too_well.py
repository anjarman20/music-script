"""All Too Well (10 Minute Version) — Taylor Swift.
Letakkan all-to-well-10minutes.mp3 di folder yang sama dengan script.
Persiapan sekali: python -m pip install pygame
Jalankan:        python all_too_well.py
Lirik saja:      python all_too_well.py --silent
Koreksi waktu:  python all_too_well.py --offset 0.3
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


TITLE = "All Too Well (10 Minute Version)"
ARTIST = "Taylor Swift"
DEFAULT_AUDIO_NAME = "all-to-well-10minutes.mp3"
EMBEDDED_LRC = '[00:00.00]\n[00:23.00]I walked through the door with you, the air was cold\n[00:28.30]But somethin\' \'bout it felt like home somehow\n[00:32.70]And I left my scarf there at your sister\'s house\n[00:37.80]And you\'ve still got it in your drawer, even now\n[00:43.70]\n[00:53.40]Oh, your sweet disposition and my wide-eyed gaze\n[00:58.90]We\'re singin\' in the car, getting lost upstate\n[01:04.60]Autumn leaves fallin\' down like pieces into place\n[01:08.70]And I can picture it after all these days\n[01:14.50]And I know it\'s long gone and\n[01:17.10]That magic\'s not here no more\n[01:19.70]And I might be okay, but I\'m not fine at all\n[01:25.10]Oh, oh, oh\n[01:30.40]\'Causе there we arе again on that little town street\n[01:34.90]You almost ran the red \'cause you were lookin\' over at me\n[01:39.80]Wind in my hair, I was there\n[01:42.30]I remember it all too well\n[01:50.10]\n[01:50.40]Photo album on the counter, your cheeks were turnin\' red\n[01:55.50]You used to be a little kid with glasses in a twin-sized bed\n[02:00.90]And your mother\'s tellin\' stories \'bout you on the tee-ball team\n[02:05.70]You taught me \'bout your past, thinkin\' your future was me\n[02:10.90]And you were tossing me the car keys, "Fuck the patriarchy"\n[02:15.30]Keychain on the ground, we were always skippin\' town\n[02:20.80]And I was thinkin\' on the drive down, "Any time now\n[02:25.10]He\'s gonna say it\'s love," you never called it what it was\n[02:30.90]\'Til we were dead and gone and buried\n[02:34.20]Check the pulse and come back swearin\' it\'s the same\n[02:38.40]After three months in the grave\n[02:40.70]And then you wondered where it went to as I reached for you\n[02:46.40]But all I felt was shame and you held my lifeless frame\n[02:52.10]And I know it\'s long gone and\n[02:55.10]There was nothing else I could do\n[02:57.70]And I forget about you long enough\n[03:00.20]To forget why I needed to\n[03:08.00]\n[03:08.30]\'Cause there we are again in the middle of the night\n[03:12.90]We\'re dancin\' \'round the kitchen in the refrigerator light\n[03:17.80]Down the stairs, I was there\n[03:20.30]I remember it all too well\n[03:28.40]\n[03:28.90]And there we are again when nobody had to know\n[03:33.60]You kept me like a secret, but I kept you like an oath\n[03:38.40]Sacred prayer and we\'d swear\n[03:41.10]To remember it all too well, yeah\n[03:50.70]\n[04:04.00]Well, maybe we got lost in translation, maybe I asked for too much\n[04:09.50]But maybe this thing was a masterpiece \'til you tore it all up\n[04:14.60]Runnin\' scared, I was there\n[04:17.10]I remember it all too well\n[04:24.90]And you call me up again just to break me like a promise\n[04:30.50]So casually cruel in the name of bein\' honest\n[04:35.20]I\'m a crumpled-up piece of paper lyin\' here\n[04:39.70]\'Cause I remember it all, all, all\n[04:45.80]They say all\'s well that ends well, but I\'m in a new hell\n[04:51.20]Every time you double-cross my mind\n[04:56.40]You said if we had been closer in age, maybe it would\'ve been fine\n[05:02.80]And that made me want to die\n[05:06.90]The idea you had of me, who was she?\n[05:09.50]A never-needy, ever-lovely jewel whose shine reflects on you\n[05:17.10]Not weepin\' in a party bathroom\n[05:19.90]Some actress askin\' me what happened, you\n[05:23.60]That\'s what happened, you\n[05:27.50]You who charmed my dad with self-effacing jokes\n[05:32.20]Sippin\' coffee like you\'re on a late-night show\n[05:37.60]But then he watched me watch the front door all night, willin\' you to come\n[05:42.40]And he said, "It\'s supposed to be fun turning twenty-one"\n[05:49.50]\n[06:01.40]Time won\'t fly, it\'s like I\'m paralyzed by it\n[06:06.10]I\'d like to be my old self again, but I\'m still tryin\' to find it\n[06:10.90]After plaid shirt days and nights when you made me your own\n[06:16.30]Now you mail back my things and I walk home alone\n[06:21.60]But you keep my old scarf from that very first week\n[06:26.50]\'Cause it reminds you of innocence and it smells like me\n[06:31.70]You can\'t get rid of it\n[06:34.20]\'Cause you remember it all too well, yeah\n[06:42.10]\'Cause there we are again when I loved you so\n[06:47.20]Back before you lost the one real thing you\'ve ever known\n[06:51.90]It was rare, I was there\n[06:54.40]I remember it all too well\n[07:01.90]Wind in my hair, you were there\n[07:04.60]You remember it all\n[07:07.60]Down the stairs, you were there\n[07:10.00]You remember it all\n[07:13.00]It was rare, I was there\n[07:15.10]I remember it all too well\n[07:21.50]And I was never good at tellin\' jokes, but the punch line goes\n[07:27.70]"I\'ll get older, but your lovers stay my age"\n[07:33.30]From when your Brooklyn broke my skin and bones\n[07:38.10]I\'m a soldier who\'s returning half her weight\n[07:43.60]And did the twin flame bruise paint you blue?\n[07:48.80]Just between us, did the love affair maim you too?\n[07:53.90]\'Cause in this city\'s barren cold\n[07:57.90]I still remember the first fall of snow\n[08:03.00]And how it glistened as it fell\n[08:07.40]I remember it all too well\n[08:12.40]\n[08:14.90]Just between us, did the love affair maim you all too well?\n[08:24.80]\n[08:25.00]Just between us, do you remember it all too well?\n[08:35.10]\n[08:35.30]Just between us, I remember it (Just between us) all too well\n[08:41.90]Wind in my hair, I was there, I was there (I was there)\n[08:46.20]Down the stairs, I was there, I was there\n[08:51.90]Sacred prayer, I was there, I was there\n[08:57.00]It was rare, you remember it all too well\n[09:01.50]Wind in my hair, I was there, I was there (Oh)\n[09:07.40]Down the stairs, I was there, I was there (I was there)\n[09:12.30]Sacred prayer, I was there, I was there\n[09:17.40]It was rare, you remember it (All too well)\n[09:22.20]Wind in my hair, I was there, I was there\n[09:28.00]Down the stairs, I was there, I was there\n[09:32.90]Sacred prayer, I was there, I was there\n[09:38.30]It was rare, you remember it\n[09:42.90]\n[09:43.20]Wind in my hair, I was there, I was there\n[09:48.40]Down the stairs, I was there, I was there\n[09:54.20]Sacred prayer, I was there, I was there\n[10:00.30]\n[10:10.30]'
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

