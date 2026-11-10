import struct
import zlib
from pathlib import Path


def make_icon(output_path: Path) -> None:
    w, h = 256, 256
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        for x in range(w):
            dx = min(x, w - 1 - x)
            dy = min(y, h - 1 - y)
            if dx < 28 and dy < 28 and (28 - dx) ** 2 + (28 - dy) ** 2 > 28 ** 2:
                raw.extend((0, 0, 0, 0))
                continue
            in_f = (
                (76 <= x <= 108 and 56 <= y <= 200)
                or (76 <= x <= 184 and 56 <= y <= 86)
                or (76 <= x <= 164 and 116 <= y <= 144)
            )
            if in_f:
                raw.extend((2, 6, 23, 255))
            else:
                r = int(16 - (y / h) * 11)
                g = int(185 - (y / h) * 35)
                b = int(129 - (y / h) * 24)
                raw.extend((r, g, b, 255))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )
    ico_header = struct.pack("<HHH", 0, 1, 1)
    ico_entry = struct.pack("<BBBBHHII", 0, 0, 0, 0, 1, 32, len(png), 6 + 16)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(ico_header + ico_entry + png)
    print(f"Created {output_path} ({output_path.stat().st_size} bytes)")


if __name__ == "__main__":
    make_icon(Path(__file__).resolve().parent / "icon.ico")
