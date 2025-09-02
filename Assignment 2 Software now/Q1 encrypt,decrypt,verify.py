import sys
import string
from typing import Dict, Tuple

LOWER = string.ascii_lowercase           # 'a'..'z'
UPPER = string.ascii_uppercase           # 'A'..'Z'
LOWER_FIRST, LOWER_SECOND = LOWER[:13], LOWER[13:]   # a-m, n-z
UPPER_FIRST, UPPER_SECOND = UPPER[:13], UPPER[13:]   # A-M, N-Z


def _shift_within_group(ch: str, shift: int, group: str) -> str:
    """Shift a character within its 13-letter group with wrap-around."""
    n = len(group)  # 13
    i = group.index(ch)
    return group[(i + shift) % n]


def build_maps(shift1: int, shift2: int) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Build encryption/decryption maps using the rules:
      - lowercase a–m: forward by (shift1 * shift2)
      - lowercase n–z: backward by (shift1 + shift2)
      - uppercase A–M: backward by shift1
      - uppercase N–Z: forward by (shift2 ** 2)
    Non-letters are left unchanged during transform (handled elsewhere).
    Returns (enc_map, dec_map).
    """
    enc_map: Dict[str, str] = {}

    # Lowercase halves
    k_low_first  = (shift1 * shift2)      # forward
    k_low_second = -(shift1 + shift2)     # backward

    for ch in LOWER_FIRST:
        enc_map[ch] = _shift_within_group(ch, k_low_first, LOWER_FIRST)
    for ch in LOWER_SECOND:
        enc_map[ch] = _shift_within_group(ch, k_low_second, LOWER_SECOND)

    # Uppercase halves
    k_up_first  = -shift1                  # backward
    k_up_second = (shift2 ** 2)            # forward

    for ch in UPPER_FIRST:
        enc_map[ch] = _shift_within_group(ch, k_up_first, UPPER_FIRST)
    for ch in UPPER_SECOND:
        enc_map[ch] = _shift_within_group(ch, k_up_second, UPPER_SECOND)

    # Inverse mapping for decryption
    dec_map = {v: k for k, v in enc_map.items()}
    return enc_map, dec_map


def transform_text(text: str, mapping: Dict[str, str]) -> str:
    """Apply the single-character mapping, leaving characters not in the map unchanged."""
    return ''.join(mapping.get(ch, ch) for ch in text)


def encrypt_file(input_path: str, output_path: str, shift1: int, shift2: int) -> None:
    """Read plaintext, encrypt, write ciphertext."""
    enc_map, _ = build_maps(shift1, shift2)
    with open(input_path, 'r', encoding='utf-8') as f:
        plain = f.read()
    cipher = transform_text(plain, enc_map)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(cipher)


def decrypt_file(input_path: str, output_path: str, shift1: int, shift2: int) -> None:
    """Read ciphertext, decrypt, write plaintext."""
    _, dec_map = build_maps(shift1, shift2)
    with open(input_path, 'r', encoding='utf-8') as f:
        cipher = f.read()
    plain = transform_text(cipher, dec_map)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(plain)


def verify_files(original_path: str, decrypted_path: str) -> bool:
    """Return True if original and decrypted files are byte-for-byte equal."""
    with open(original_path, 'r', encoding='utf-8') as f1, open(decrypted_path, 'r', encoding='utf-8') as f2:
        return f1.read() == f2.read()


def main() -> None:
    """Prompt for shifts, run encrypt → decrypt → verify with fixed paths."""
    try:
        shift1 = int(input("Enter shift1 (integer): ").strip())
        shift2 = int(input("Enter shift2 (integer): ").strip())
    except Exception:
        print("Invalid input. Please enter integers for shift1 and shift2.")
        sys.exit(1)

    in_path  = "raw_text.txt"
    enc_path = "encrypted_text.txt"
    dec_path = "decrypted_text.txt"

    try:
        encrypt_file(in_path, enc_path, shift1, shift2)
        print(f"Encrypted -> {enc_path}")

        decrypt_file(enc_path, dec_path, shift1, shift2)
        print(f"Decrypted -> {dec_path}")

        ok = verify_files(in_path, dec_path)
        print("Verification:", "SUCCESS" if ok else "FAILED")
    except FileNotFoundError as e:
        print("File not found:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
