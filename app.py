import random
import re
from typing import Dict, List, Tuple
import streamlit as st

# ==============================================================================
# 1. PAGE CONFIGURATION & HISTORICAL STYLING
# ==============================================================================
st.set_page_config(
    page_title="TJ — Thomas Jefferson Wheel Cipher",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    /* Historical Colonial & Brass Aesthetic */
    .main-header {
        font-family: 'Georgia', serif;
        color: #2c1e14;
        border-bottom: 2px solid #8b6f47;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-family: 'Georgia', serif;
        color: #5c4632;
        font-style: italic;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .cylinder-container {
        overflow-x: auto;
        background: #fdfaf5;
        border: 2px solid #8b6f47;
        border-radius: 8px;
        padding: 12px;
        box-shadow: inset 0 2px 6px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    table.cylinder-table {
        border-collapse: collapse;
        width: 100%;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.92rem;
        text-align: center;
    }
    table.cylinder-table th {
        background-color: #3d2b1f;
        color: #f4ebd9;
        padding: 6px 4px;
        border: 1px solid #5c4632;
        font-size: 0.78rem;
    }
    table.cylinder-table td {
        padding: 4px 5px;
        border: 1px solid #dccbb5;
        color: #3b2d22;
        font-weight: 600;
    }
    tr.row-index-0 td {
        background-color: #e6d3b3 !important;
        color: #1f140e !important;
        font-weight: 800 !important;
        border-top: 2px solid #5c4632 !important;
        border-bottom: 2px solid #5c4632 !important;
    }
    tr.row-cipher td {
        background-color: #cfe2f3 !important;
        color: #0b2e4f !important;
        font-weight: 800 !important;
        border-top: 2px solid #2b5c8f !important;
        border-bottom: 2px solid #2b5c8f !important;
    }
    tr.row-decrypted td {
        background-color: #d4edda !important;
        color: #155724 !important;
        font-weight: 800 !important;
        border-top: 2px solid #28a745 !important;
        border-bottom: 2px solid #28a745 !important;
    }
    .row-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-weight: bold;
    }
    .wheel-card {
        background: #f7f1e5;
        border: 1px solid #c8b496;
        border-radius: 6px;
        padding: 6px;
        text-align: center;
        font-family: 'Courier New', monospace;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 2. HISTORICAL & RANDOMIZED 36-WHEEL DEFINITIONS
# ==============================================================================
# 36 deterministic, unique 26-letter permutations representing Jefferson's
# numbered boxwood disks (1 through 36), generated from a fixed historical seed
# so senders and recipients share the same canonical set of 36 wheels by default.
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def generate_canonical_wheels(seed: int = 1795) -> Dict[int, str]:
    """Generates 36 unique, deterministic 26-letter alphabet permutations (seeded to 1795,

    the era Jefferson invented the wheel cipher while serving as Secretary of
    State).
    """
    rng = random.Random(seed)
    wheels: Dict[int, str] = {}
    used = set()
    for disk_id in range(1, 37):
        while True:
            chars = list(ALPHABET)
            rng.shuffle(chars)
            perm = "".join(chars)
            if perm not in used:
                used.add(perm)
                wheels[disk_id] = perm
                break
    return wheels


# Common English bigrams, trigrams, and words for automatic plaintext row detection
COMMON_NGRAMS = (
    "THE",
    "AND",
    "ING",
    "ENT",
    "ION",
    "HER",
    "FOR",
    "THA",
    "NTH",
    "INT",
    "ERE",
    "TIO",
    "TER",
    "EST",
    "ERS",
    "ATI",
    "HAT",
    "ATE",
    "ALL",
    "ETH",
    "HES",
    "VER",
    "HIS",
    "OFT",
    "ITH",
    "FTH",
    "STH",
    "OTH",
    "RES",
    "ONT",
    "ARE",
    "WAS",
    "YOU",
    "NOT",
    "HAVE",
    "THIS",
    "WITH",
    "FROM",
    "THEY",
    "WILL",
    "MEET",
    "DAWN",
    "MONTICELLO",
    "LIBERTY",
    "JEFFERSON",
    "ATTACK",
    "SECRET",
    "MESSAGE",
    "THOMAS",
    "CIPHER",
    "WHEEL",
    "ORDER",
    "FREEDOM",
    "PHILADELPHIA",
    "VIRGINIA",
    "TH",
    "HE",
    "IN",
    "ER",
    "AN",
    "RE",
    "ON",
    "AT",
    "EN",
    "ND",
    "TI",
    "ES",
    "OR",
    "TE",
    "OF",
    "ED",
    "IS",
    "IT",
    "AL",
    "AR",
    "ST",
    "TO",
    "NT",
    "NG",
)

ENGLISH_LETTER_FREQ = {
    "E": 12.7,
    "T": 9.1,
    "A": 8.2,
    "O": 7.5,
    "I": 7.0,
    "N": 6.7,
    "S": 6.3,
    "H": 6.1,
    "R": 6.0,
    "D": 4.3,
    "L": 4.0,
    "C": 2.8,
    "U": 2.8,
    "M": 2.4,
    "W": 2.4,
    "F": 2.2,
    "G": 2.0,
    "Y": 2.0,
    "P": 1.9,
    "B": 1.5,
    "V": 1.0,
    "K": 0.8,
    "J": 0.15,
    "X": 0.15,
    "Q": 0.10,
    "Z": 0.07,
}


# ==============================================================================
# 3. CORE CYLINDER & MODULAR ROTATION LOGIC
# ==============================================================================
def rotate_wheel_string(wheel_alphabet: str, offset: int) -> str:
    """Rotates a 26-character wheel alphabet using modular arithmetic ((i + offset) % 26)

    so spinning the wheel wraps smoothly from Z back to A.
    """
    mod_offset = offset % 26
    return wheel_alphabet[mod_offset:] + wheel_alphabet[:mod_offset]


def sanitize_to_36_letters(text: str, pad_char: str = "X") -> str:
    """Strips non-alphabetic characters, uppercases, and pads or truncates to 36 letters."""
    cleaned = re.sub(r"[^A-Za-z]", "", text).upper()
    if len(cleaned) < 36:
        # Repeat a deterministic filler or pad_char if shorter than 36
        cleaned = cleaned.ljust(36, pad_char)
    return cleaned[:36]


def align_cylinder_to_text(
    wheels: Dict[int, str], disk_order: List[int], target_text: str
) -> List[int]:
    """Calculates the 36 rotational offsets (0..25) so that Row 0 of the active spindle

    spells `target_text` across the ordered disks.
    """
    clean_target = sanitize_to_36_letters(target_text)
    offsets: List[int] = []
    for pos, disk_id in enumerate(disk_order):
        wheel_str = wheels[disk_id]
        target_char = clean_target[pos]
        char_index = wheel_str.index(target_char)
        offsets.append(char_index)
    return offsets


def get_cylinder_rows(
    wheels: Dict[int, str], disk_order: List[int], offsets: List[int]
) -> List[str]:
    """Returns all 26 horizontal rows across the 36 aligned wheels."""
    rotated_wheels = [
        rotate_wheel_string(wheels[disk_id], offsets[idx])
        for idx, disk_id in enumerate(disk_order)
    ]
    rows = []
    for row_idx in range(26):
        row_str = "".join(
            rotated_wheels[col_idx][row_idx] for col_idx in range(36)
        )
        rows.append(row_str)
    return rows


def score_english_readability(text: str) -> float:
    """Scores a 36-character row for English readability using letter frequency

    and common English n-gram matches.
    """
    score = sum(ENGLISH_LETTER_FREQ.get(ch, 0.0) for ch in text)
    for ngram in COMMON_NGRAMS:
        count = text.count(ngram)
        if count > 0:
            score += count * (len(ngram) ** 2.2) * 4.5
    return round(score, 2)


def parse_disk_order(order_str: str) -> Tuple[bool, List[int], str]:
    """Parses a comma- or space-separated string of 36 integers (1..36) and validates

    that it is a valid permutation of disks 1 through 36.
    """
    tokens = [t for t in re.split(r"[\s,;]+", order_str.strip()) if t]
    try:
        nums = [int(t) for t in tokens]
    except ValueError:
        return (
            False,
            [],
            "Disk order must contain only integers separated by commas or"
            " spaces.",
        )

    if len(nums) != 36:
        return (
            False,
            [],
            f"Expected 36 disk numbers (1–36), but received {len(nums)}.",
        )

    if sorted(nums) != list(range(1, 37)):
        missing = sorted(set(range(1, 37)) - set(nums))
        return (
            False,
            [],
            "Disk order must contain each disk 1 through 36 exactly once."
            f" Missing: {missing}",
        )

    return True, nums, ""


# ==============================================================================
# 4. SESSION STATE INITIALIZATION
# ==============================================================================
if "wheels" not in st.session_state:
    st.session_state.wheels = generate_canonical_wheels(seed=1795)

if "disk_order" not in st.session_state:
    st.session_state.disk_order = list(range(1, 37))

if "default_plaintext" not in st.session_state:
    st.session_state.default_plaintext = "MEETMEATMONTICELLOATSUNRISEWITHPLANS"

if "offsets" not in st.session_state:
    st.session_state.offsets = align_cylinder_to_text(
        st.session_state.wheels,
        st.session_state.disk_order,
        st.session_state.default_plaintext,
    )

if "cipher_row_offset" not in st.session_state:
    st.session_state.cipher_row_offset = 7

if "shared_ciphertext" not in st.session_state:
    initial_rows = get_cylinder_rows(
        st.session_state.wheels,
        st.session_state.disk_order,
        st.session_state.offsets,
    )
    st.session_state.shared_ciphertext = initial_rows[
        st.session_state.cipher_row_offset
    ]

if "shared_disk_order_str" not in st.session_state:
    st.session_state.shared_disk_order_str = ", ".join(
        str(d) for d in st.session_state.disk_order
    )


# ==============================================================================
# 5. SIDEBAR: SPINDLE & DISK ORDER CONFIGURATION
# ==============================================================================
with st.sidebar:
    st.markdown("## ⚙️ Spindle & Disk Key")
    st.caption(
        "In Thomas Jefferson's 1795 cipher, both sender and recipient share 36"
        " numbered wooden disks (1–36) threaded onto an iron spindle in a"
        " secret sequence."
    )

    order_input = st.text_area(
        "Active Disk Sequence (1–36)",
        value=", ".join(str(x) for x in st.session_state.disk_order),
        height=95,
        help=(
            "Enter the 36 disk numbers in the exact order they are mounted on"
            " the spindle."
        ),
    )

    col_apply, col_rand = st.columns(2)
    with col_apply:
        if st.button("Apply Order", use_container_width=True):
            valid, parsed_order, err_msg = parse_disk_order(order_input)
            if valid:
                st.session_state.disk_order = parsed_order
                st.session_state.shared_disk_order_str = ", ".join(
                    str(d) for d in parsed_order
                )
                st.success("Spindle order updated!")
                st.rerun()
            else:
                st.error(err_msg)

    with col_rand:
        if st.button("Shuffle Disks", use_container_width=True):
            shuffled = list(range(1, 37))
            random.shuffle(shuffled)
            st.session_state.disk_order = shuffled
            st.session_state.shared_disk_order_str = ", ".join(
                str(d) for d in shuffled
            )
            st.rerun()

    if st.button("Reset to Canonical Order (1–36)", use_container_width=True):
        st.session_state.disk_order = list(range(1, 37))
        st.session_state.shared_disk_order_str = ", ".join(
            str(d) for d in st.session_state.disk_order
        )
        st.rerun()

    st.divider()
    st.markdown("### 🎲 Wheel Alphabet Seed")
    seed_val = st.number_input(
        "Alphabet Permutation Seed",
        min_value=1,
        max_value=999999,
        value=1795,
        step=1,
        help=(
            "Default 1795 generates the canonical 36 unique wheel alphabets."
            " Change to generate a completely new set of 36 disks."
        ),
    )
    if st.button("Regenerate 36 Disks", use_container_width=True):
        st.session_state.wheels = generate_canonical_wheels(seed=int(seed_val))
        st.session_state.offsets = align_cylinder_to_text(
            st.session_state.wheels,
            st.session_state.disk_order,
            st.session_state.default_plaintext,
        )
        st.success(f"Generated 36 new wheel permutations (Seed {seed_val}).")
        st.rerun()

    with st.expander("🔍 Inspect All 36 Wheel Permutations"):
        for d_id in range(1, 37):
            st.code(
                f"Disk {d_id:02d}: {st.session_state.wheels[d_id]}",
                language=None,
            )


# ==============================================================================
# 6. HEADER & APPLICATION TABS
# ==============================================================================
st.markdown(
    "<h1 class='main-header'>🏛️ TJ — The Thomas Jefferson Wheel Cipher</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div class='subtitle'>Interactive 36-Disk Polyalphabetic Cylinder"
    " Simulator (c. 1795) — Align rings, spin individual disks with modular"
    " wrap-around, encode dispatches, and scan the cylinder to decipher"
    " hidden messages.</div>",
    unsafe_allow_html=True,
)

tab_sender, tab_receiver, tab_cylinder = st.tabs([
    "🖋️ 1. Sender: Align & Encode Dispatch",
    "🔎 2. Recipient: Input Ciphertext & Decipher",
    "🎡 3. Interactive 36-Wheel Cylinder & Manual Rotation",
])


# ==============================================================================
# TAB 1: SENDER WORKFLOW (ALIGN RINGS -> PICK CIPHERTEXT ROW)
# ==============================================================================
with tab_sender:
    st.subheader("Sender Mode: Align the 36 Rings & Select a Cipher Row")
    st.write(
        "Just as Jefferson described, enter a message up to 36 letters to align"
        " **Row 0 (Alignment Guide Bar)**, then choose any of the other 25 rows"
        " on the cylinder to transmit as your ciphertext."
    )

    col_msg, col_pad, col_row = st.columns([3, 1, 1.5])
    with col_msg:
        sender_plaintext = st.text_input(
            "Plaintext Message (up to 36 letters; non-letters are stripped automatically)",
            value=st.session_state.default_plaintext,
            max_chars=60,
        )
    with col_pad:
        pad_letter = st.selectbox(
            "Padding Letter",
            options=list(ALPHABET),
            index=23,  # 'X'
            help=(
                "Used to fill remaining disks if your message is under 36"
                " letters."
            ),
        )
    with col_row:
        selected_cipher_row = st.slider(
            "Select Ciphertext Row Offset (1–25)",
            min_value=1,
            max_value=25,
            value=st.session_state.cipher_row_offset,
            help=(
                "Row 0 holds your plaintext. Pick any other row (1–25) as the"
                " ciphertext to send."
            ),
        )

    cleaned_sender_text = sanitize_to_36_letters(
        sender_plaintext, pad_char=pad_letter
    )
    sender_offsets = align_cylinder_to_text(
        st.session_state.wheels,
        st.session_state.disk_order,
        cleaned_sender_text,
    )
    sender_rows = get_cylinder_rows(
        st.session_state.wheels, st.session_state.disk_order, sender_offsets
    )
    generated_ciphertext = sender_rows[selected_cipher_row]

    c1, c2 = st.columns(2)
    with c1:
        st.info(
            "**Row 00 (Aligned Plaintext across 36"
            f" Disks):**\n\n`{sender_rows[0]}`"
        )
    with c2:
        st.warning(
            f"**Row {selected_cipher_row:02d} (Selected Ciphertext to"
            f" Transmit):**\n\n`{generated_ciphertext}`"
        )

    if st.button(
        "📨 Lock Cylinder & Send Dispatch to Recipient Tab",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.default_plaintext = cleaned_sender_text
        st.session_state.offsets = sender_offsets
        st.session_state.cipher_row_offset = selected_cipher_row
        st.session_state.shared_ciphertext = generated_ciphertext
        st.session_state.shared_disk_order_str = ", ".join(
            str(d) for d in st.session_state.disk_order
        )
        st.success(
            "Cylinder aligned and dispatch loaded into the **Recipient**"
            " and **Interactive Cylinder** tabs!"
        )

    st.markdown("#### Outgoing Dispatch Packet (Share with Recipient)")
    dispatch_col1, dispatch_col2 = st.columns([1.2, 2])
    with dispatch_col1:
        st.code(f"Ciphertext (36 chars):\n{generated_ciphertext}", language=None)
    with dispatch_col2:
        st.code(
            "Spindle Disk Order (1-36):\n"
            + ", ".join(str(d) for d in st.session_state.disk_order),
            language=None,
        )


# ==============================================================================
# TAB 2: RECIPIENT WORKFLOW (INPUT CIPHERTEXT -> SCAN & HIGHLIGHT READABLE ROW)
# ==============================================================================
with tab_receiver:
    st.subheader(
        "Recipient Mode: Align Cylinder to Ciphertext & Scan for Plaintext"
    )
    st.write(
        "Enter the 36-letter ciphertext and the agreed-upon disk order. **TJ**"
        " aligns the 36 wheels so the ciphertext sits on **Row 00**, then"
        " evaluates all 25 remaining rows around the cylinder to automatically"
        " highlight the deciphered readable message."
    )

    rec_col1, rec_col2 = st.columns([1.5, 1.5])
    with rec_col1:
        cipher_input = st.text_input(
            "Input 36-Letter Ciphertext Row",
            value=st.session_state.shared_ciphertext,
            help=(
                "Paste the 36-character ciphertext received from the sender."
            ),
        )
    with rec_col2:
        rec_order_input = st.text_input(
            "Recipient Spindle Disk Order (36 Disks)",
            value=st.session_state.shared_disk_order_str,
            help=(
                "Comma-separated permutation of disks 1–36 matching the"
                " sender's key."
            ),
        )

    valid_rec_order, rec_disk_order, rec_order_err = parse_disk_order(
        rec_order_input
    )
    if not valid_rec_order:
        st.error(rec_order_err)
    else:
        clean_cipher_in = sanitize_to_36_letters(cipher_input, pad_char="X")
        rec_offsets = align_cylinder_to_text(
            st.session_state.wheels, rec_disk_order, clean_cipher_in
        )
        rec_rows = get_cylinder_rows(
            st.session_state.wheels, rec_disk_order, rec_offsets
        )

        # Score all 25 candidate rows (Rows 1..25) to identify the most readable English row
        scored_rows = []
        for r_idx in range(1, 26):
            r_text = rec_rows[r_idx]
            r_score = score_english_readability(r_text)
            scored_rows.append((r_idx, r_text, r_score))

        best_row_idx, best_row_text, best_row_score = max(
            scored_rows, key=lambda item: item[2]
        )

        # Allow recipient to inspect or override the highlighted plaintext row
        ctrl_col1, ctrl_col2 = st.columns([2.2, 1])
        with ctrl_col1:
            st.success(
                f"🔓 **Auto-Detected Readable Plaintext at Row +{best_row_idx:02d}**"
                f" (Readability Score: {best_row_score}):\n\n### `{best_row_text}`"
            )
        with ctrl_col2:
            manual_highlight_row = st.number_input(
                "Inspect / Highlight Specific Row (1–25)",
                min_value=1,
                max_value=25,
                value=int(best_row_idx),
                step=1,
                help=(
                    "Auto-selected based on English readability. Step through"
                    " rows 1–25 to visually scan the cylinder yourself."
                ),
            )
            if st.button(
                "Sync Receiver Alignment to Main Cylinder",
                use_container_width=True,
            ):
                st.session_state.disk_order = rec_disk_order
                st.session_state.offsets = rec_offsets
                st.success(
                    "Main 36-wheel cylinder synced to Recipient alignment!"
                )

        # Build full 26-row visual cylinder table for scanning
        st.markdown("#### Full 26-Row Cylinder Scan")
        table_html = [
            "<div class='cylinder-container'><table class='cylinder-table'>"
        ]
        # Header row: Position 1..36 and Disk ID
        header_cells = ["<th>Row</th>", "<th>Role / Score</th>"]
        for pos_idx, d_id in enumerate(rec_disk_order, start=1):
            header_cells.append(f"<th>#{pos_idx}<br>(D{d_id})</th>")
        table_html.append("<thead><tr>" + "".join(header_cells) + "</tr></thead>")

        table_html.append("<tbody>")
        for r_idx, r_str in enumerate(rec_rows):
            if r_idx == 0:
                row_class = "row-cipher"
                role_label = "🔒 Ciphertext (Row 00)"
            elif r_idx == manual_highlight_row:
                row_class = "row-decrypted"
                r_sc = score_english_readability(r_str)
                role_label = f"🔓 Plaintext (+{r_idx:02d}) ★ {r_sc}"
            else:
                row_class = ""
                r_sc = score_english_readability(r_str)
                role_label = f"Row +{r_idx:02d} ({r_sc})"

            char_cells = "".join(f"<td>{ch}</td>" for ch in r_str)
            table_html.append(
                f"<tr class='{row_class}'><td><b>+{r_idx:02d}</b></td>"
                f"<td style='white-space:nowrap;'>{role_label}</td>{char_cells}</tr>"
            )
        table_html.append("</tbody></table></div>")
        st.markdown("".join(table_html), unsafe_allow_html=True)


# ==============================================================================
# TAB 3: INTERACTIVE 36-WHEEL CYLINDER & INDIVIDUAL MODULAR ROTATION
# ==============================================================================
with tab_cylinder:
    st.subheader("Interactive 36-Wheel Cylinder Simulator")
    st.write(
        "Rotate each of the 36 wheels independently using modular arithmetic"
        " (`(offset ± 1) mod 26` so `Z` wraps smoothly to `A`), or spin the"
        " entire cylinder simultaneously."
    )

    # Global cylinder controls
    g_col1, g_col2, g_col3, g_col4 = st.columns(4)
    with g_col1:
        if st.button(
            "🔼 Rotate All 36 Wheels Up (-1 mod 26)", use_container_width=True
        ):
            st.session_state.offsets = [
                (o - 1) % 26 for o in st.session_state.offsets
            ]
            st.rerun()
    with g_col2:
        if st.button(
            "🔽 Rotate All 36 Wheels Down (+1 mod 26)", use_container_width=True
        ):
            st.session_state.offsets = [
                (o + 1) % 26 for o in st.session_state.offsets
            ]
            st.rerun()
    with g_col3:
        if st.button("🔀 Scramble All Wheel Rotations", use_container_width=True):
            st.session_state.offsets = [random.randint(0, 25) for _ in range(36)]
            st.rerun()
    with g_col4:
        if st.button("📏 Reset All Wheel Offsets to 0", use_container_width=True):
            st.session_state.offsets = [0] * 36
            st.rerun()

    # Individual 36-Wheel Bank Controls (3 banks of 12 wheels for clean layout)
    st.markdown("#### Individual Wheel Controls (Disks 1–36 on Spindle)")
    bank_tabs = st.tabs([
        "Wheels 1 – 12",
        "Wheels 13 – 24",
        "Wheels 25 – 36",
    ])

    for bank_idx, bank_tab in enumerate(bank_tabs):
        with bank_tab:
            start_pos = bank_idx * 12
            cols = st.columns(12)
            for i in range(12):
                pos = start_pos + i
                disk_id = st.session_state.disk_order[pos]
                wheel_alpha = st.session_state.wheels[disk_id]
                cur_offset = st.session_state.offsets[pos]
                rotated = rotate_wheel_string(wheel_alpha, cur_offset)

                with cols[i]:
                    st.markdown(
                        f"<div class='wheel-card'><b>#{pos+1}</b><br><small>Disk"
                        f" {disk_id:02d}</small></div>",
                        unsafe_allow_html=True,
                    )
                    if st.button(
                        "▲",
                        key=f"up_{pos}",
                        help=f"Rotate wheel #{pos+1} (Disk {disk_id}) up (-1 mod 26)",
                        use_container_width=True,
                    ):
                        st.session_state.offsets[pos] = (cur_offset - 1) % 26
                        st.rerun()

                    # Show window around Row 00 (-2 to +2)
                    prev2 = rotated[-2]
                    prev1 = rotated[-1]
                    curr0 = rotated[0]
                    next1 = rotated[1]
                    next2 = rotated[2]
                    st.markdown(
                        f"<div style='text-align:center;font-family:Courier"
                        f" New,monospace;line-height:1.35;'>"
                        f"<span style='color:#9e8c76;'>{prev2}</span><br>"
                        f"<span style='color:#6e5a44;'>{prev1}</span><br>"
                        f"<span style='background:#e6d3b3;color:#1f140e;font-weight:bold;padding:2px"
                        f" 6px;border-radius:3px;border:1px solid"
                        f" #5c4632;'>{curr0}</span><br>"
                        f"<span style='color:#6e5a44;'>{next1}</span><br>"
                        f"<span style='color:#9e8c76;'>{next2}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                    if st.button(
                        "▼",
                        key=f"down_{pos}",
                        help=f"Rotate wheel #{pos+1} (Disk {disk_id}) down (+1 mod 26)",
                        use_container_width=True,
                    ):
                        st.session_state.offsets[pos] = (cur_offset + 1) % 26
                        st.rerun()
                    st.caption(f"idx:{cur_offset:02d}")

    # Full 26x36 Cylinder Matrix View
    current_rows = get_cylinder_rows(
        st.session_state.wheels,
        st.session_state.disk_order,
        st.session_state.offsets,
    )
    st.markdown("#### Complete 36-Wheel × 26-Row Cylinder View")
    st.caption(
        "**Row +00** (gold) is the active alignment bar. **Row"
        f" +{st.session_state.cipher_row_offset:02d}** (blue) is the currently"
        " selected ciphertext offset."
    )

    cyl_html = [
        "<div class='cylinder-container'><table class='cylinder-table'>"
    ]
    h_cells = ["<th>Row</th>"] + [
        f"<th>#{p}<br><small>D{d}</small></th>"
        for p, d in enumerate(st.session_state.disk_order, start=1)
    ]
    cyl_html.append("<thead><tr>" + "".join(h_cells) + "</tr></thead><tbody>")

    for r_i, r_str in enumerate(current_rows):
        if r_i == 0:
            r_cls = "row-index-0"
            r_tag = "+00 (Guide)"
        elif r_i == st.session_state.cipher_row_offset:
            r_cls = "row-cipher"
            r_tag = f"+{r_i:02d} (Cipher)"
        else:
            r_cls = ""
            r_tag = f"+{r_i:02d}"
        cells = "".join(f"<td>{c}</td>" for c in r_str)
        cyl_html.append(
            f"<tr class='{r_cls}'><td style='white-space:nowrap;'>{r_tag}</td>{cells}</tr>"
        )
    cyl_html.append("</tbody></table></div>")
    st.markdown("".join(cyl_html), unsafe_allow_html=True)