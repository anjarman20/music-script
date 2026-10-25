"""Cinta Itu Buta — Armada

Pemakaian:
    python cinta_itu_buta.py --txt lirik.txt
    python cinta_itu_buta.py --lrc cinta_itu_buta.lrc --from-start
    python cinta_itu_buta.py --lrc cinta_itu_buta.lrc --preview
"""

import argparse
import math
import re
import sys
import time
from pathlib import Path


TITLE = "Cinta Itu Buta"
ARTIST = "Armada"
LINES = []


def load_lrc(path):
    rows = []
    offset = 0.0
    pattern = re.compile(r"\[(\d+):([0-5]?\d(?:\.\d+)?)\]")
    for raw in Path(path).read_text(encoding="utf-8-sig").splitlines():
        setting = re.fullmatch(r"\[offset:([+-]?\d+)\]", raw.strip(), re.I)
        if setting:
            offset = int(setting[1]) / 1000
            continue
        matches = list(pattern.finditer(raw))
        if not matches:
            continue
        lyric = raw[matches[-1].end():].strip()
        for match in matches:
            rows.append((int(match[1]) * 60 + float(match[2]), lyric))
    rows.sort(key=lambda row: row[0])
    if not rows:
        raise ValueError("File LRC tidak memiliki baris bertimestamp.")
    if any(a[0] == b[0] for a, b in zip(rows, rows[1:])):
        raise ValueError("Timestamp ganda: gabungkan teks pada waktu yang sama.")
    return [
        (start + offset,
         min(start + 4.0, rows[i + 1][0]) + offset
         if i + 1 < len(rows) else start + 4.0 + offset,
         lyric)
        for i, (start, lyric) in enumerate(rows)
    ]


def load_txt(path, duration=4.0, gap=0.6):
    """Buat jadwal perkiraan untuk TXT: satu baris lirik per baris."""
    lyrics = [
        line.strip()
        for line in Path(path).read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    if not lyrics:
        raise ValueError("File TXT belum berisi teks.")
    return [
        (i * (duration + gap), i * (duration + gap) + duration, lyric)
        for i, lyric in enumerate(lyrics)
    ]


def validate(lines):
    if not lines:
        raise ValueError("Belum ada lirik. Gunakan --txt, --lrc, atau isi LINES.")
    previous_end = -float("inf")
    for start, end, lyric in lines:
        if not math.isfinite(start) or not math.isfinite(end):
            raise ValueError("Waktu harus berupa angka yang valid.")
        if end <= start or start < previous_end:
            raise ValueError(
                "Waktu selesai harus setelah mulai; entri tidak boleh bertumpuk."
            )
        if not isinstance(lyric, str):
            raise ValueError("Lirik harus berupa teks.")
        previous_end = end


def wait_until(deadline):
    while True:
        remaining = deadline - time.perf_counter()
        if remaining <= 0:
            return
        time.sleep(min(remaining, 0.02))


def play(lines, offset=0.0):
    origin = time.perf_counter()
    for start, end, lyric in lines:
        wait_until(origin + start + offset)
        interval = (end - start) / max(len(lyric) - 1, 1)
        for index, char in enumerate(lyric):
            wait_until(origin + start + offset + index * interval)
            print(char, end="", flush=True)
        print(flush=True)


def main():
    parser = argparse.ArgumentParser(
        description=TITLE + " — " + ARTIST + " | efek ketik lirik di terminal.",
        epilog=(
            "Lirik dan audio tidak disertakan. TXT memakai timing perkiraan; "
            "LRC mengikuti timestamp Anda, dengan durasi ketik perkiraan. "
            "Putar audio secara terpisah."
        ),
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--lrc", help="File lirik LRC bertimestamp.")
    source.add_argument("--txt", help="File TXT: satu baris lirik per baris.")
    parser.add_argument(
        "--from-start", action="store_true",
        help="Mulai timer dari awal audio, bukan dari baris pertama.",
    )
    parser.add_argument(
        "--preview", action="store_true",
        help="Cetak seluruh teks tanpa menunggu.",
    )
    parser.add_argument(
        "--offset", type=float, default=0.0,
        help="Geser timing (detik): positif lebih lambat, negatif lebih cepat.",
    )
    parser.add_argument(
        "--line-duration", type=float, default=4.0, metavar="DETIK",
        help="Durasi ketik per baris TXT (default: 4).",
    )
    parser.add_argument(
        "--gap", type=float, default=0.6, metavar="DETIK",
        help="Jeda antarbaris TXT (default: 0.6).",
    )
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
        else:
            lines = LINES

        if not lines and not args.lrc and not args.txt:
            parser.print_help()
            print(
                "\nContoh: python cinta_itu_buta.py --txt lirik.txt\n"
                "Isi lirik.txt dengan teks yang ingin Bos tampilkan."
            )
            return 0

        validate(lines)
        width = 34
        print("=" * width)
        print(TITLE.center(width))
        print(ARTIST.center(width))
        print("=" * width)
        print(flush=True)

        if args.preview:
            print("\n".join(row[2] for row in lines))
            return 0
        if not args.from_start:
            first_start = lines[0][0]
            lines = [
                (start - first_start, end - first_start, lyric)
                for start, end, lyric in lines
            ]
        play(lines, args.offset)
    except KeyboardInterrupt:
        print("\nDihentikan.")
        return 130
    except (OSError, ValueError) as exc:
        print("Error: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

