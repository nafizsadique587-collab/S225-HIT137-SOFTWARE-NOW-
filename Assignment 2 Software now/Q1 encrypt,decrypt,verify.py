
import sys
import string

def build_maps(shift1: int, shift2: int):
    """Return (enc_map, dec_map) dicts for single-character mappings using within-half wrapping."""
    enc_map = {}
    letters_lower = string.ascii_lowercase  # 'a'..'z'
    letters_upper = string.ascii_uppercase  # 'A'..'Z'

    # Half alphabets
    low_first = letters_lower[:13]  # a-m
    low_second = letters_lower[13:] # n-z
    up_first = letters_upper[:13]   # A-M
    up_second = letters_upper[13:]  # N-Z

    def shift_in_group(ch, shift, group):
        n = len(group)  # 13
        idx = group.index(ch)
        return group[(idx + shift) % n]

    # Lowercase rules
    for ch in low_first:
        k = (shift1 * shift2)  # forward
        enc_map[ch] = shift_in_group(ch, k, low_first)
    for ch in low_second:
        k = -(shift1 + shift2)  # backward
        enc_map[ch] = shift_in_group(ch, k, low_second)

    # Uppercase rules
    for ch in up_first:
        k = -shift1  # backward
        enc_map[ch] = shift_in_group(ch, k, up_first)
    for ch in up_second:
        k = (shift2 ** 2)  # forward
        enc_map[ch] = shift_in_group(ch, k, up_second)

    # Inverse map for decryption
    dec_map = {v: k for k, v in enc_map.items()}
    return enc_map, dec_map

def transform_text(text: str, mapping: dict) -> str:
    return ''.join(mapping.get(ch, ch) for ch in text)

def encrypt_file(input_path: str, output_path: str, shift1: int, shift2: int):
    enc_map, _ = build_maps(shift1, shift2)
    with open(input_path, 'r', encoding='utf-8') as f:
        plain = f.read()
    cipher = transform_text(plain, enc_map)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(cipher)

def decrypt_file(input_path: str, output_path: str, shift1: int, shift2: int):
    _, dec_map = build_maps(shift1, shift2)
    with open(input_path, 'r', encoding='utf-8') as f:
        cipher = f.read()
    plain = transform_text(cipher, dec_map)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(plain)

def verify_files(original_path: str, decrypted_path: str) -> bool:
    with open(original_path, 'r', encoding='utf-8') as f1, open(decrypted_path, 'r', encoding='utf-8') as f2:
        return f1.read() == f2.read()

def main():
    try:
        shift1 = int(input("Enter shift1 (integer): ").strip())
        shift2 = int(input("Enter shift2 (integer): ").strip())
    except Exception:
        print("Invalid input. Please enter integers for shift1 and shift2.")
        sys.exit(1)

    in_path = "raw_text.txt"
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
