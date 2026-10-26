TJ — The Thomas Jefferson Wheel Cipher
TJ is an interactive Python Streamlit application that simulates Thomas Jefferson's 1795 polyalphabetic wheel cipher (also known as the Jefferson Cylinder or Bazeries Cylinder). It models 36 numbered wooden disks threaded onto a central iron spindle, each inscribed with a unique randomized permutation of the 26-letter alphabet.
Historical Background & How It Works
While serving as President George Washington's Secretary of State in the early 1790s, Thomas Jefferson invented a mechanical cipher cylinder consisting of 36 wooden wheels (numbered ⁠1⁠ through ⁠36⁠) mounted on a central spindle:
1. Shared Spindle Key: Both the sender and the recipient possess an identical set of 36 numbered disks and agree beforehand on the secret order in which the 36 disks are threaded onto the spindle.
2. Sender Encoding: The sender rotates the 36 disks so that a 36-letter plaintext message appears horizontally along the alignment guide bar (Row 00). The sender then locks the cylinder, picks any other horizontal row (⁠Row 01⁠ to ⁠Row 25⁠), copies down those 36 scrambled letters as the ciphertext, and sends it to the recipient.
3. Recipient Deciphering: The recipient arranges their 36 disks in the agreed spindle order and rotates each disk until the received 36-letter ciphertext is aligned along Row 00. The recipient then turns the entire cylinder and visually scans the remaining 25 rows until a single row jumps out in readable English plaintext.
Key Features
￼ 36 Unique Alphabet Disks: Generates 36 distinct 26-letter alphabet permutations seeded to ⁠1795⁠ by default so senders and recipients share the same canonical set of disks (⁠1–36⁠), with support for custom permutation seeds.
￼ Custom Spindle Key Management: Configure, validate, shuffle, or reset the 36-disk spindle order (⁠1–36⁠) from the sidebar.
￼ Sender Dispatch Mode: Enter any plaintext message up to 36 characters, automatically strip non-letters and pad shorter messages, select any ciphertext row offset (⁠1–25⁠), and generate a shareable dispatch packet.
￼ Recipient Auto-Deciphering & Cylinder Scan: Input a 36-character ciphertext and spindle order to align Row 00. TJ evaluates all 25 remaining rows using English letter-frequency and common n-gram scoring to automatically detect and highlight the deciphered plaintext row across the full 26×36 cylinder table.
￼ Interactive 36-Wheel Cylinder: Rotate individual disks up or down (⁠▲⁠ / ⁠▼⁠) across three 12-wheel banks or spin all 36 wheels simultaneously using modular arithmetic (⁠(offset ± 1) % 26⁠) so letters wrap smoothly between ⁠Z⁠ and ⁠A⁠.
Project Files
File
Description
tj_wheel_cipher.py
Main Streamlit application containing the 36-wheel generator, modular rotation engine, sender/recipient workflows, and interactive cylinder UI
requirements.txt
Python package dependencies required to run the application
README.md
Documentation, setup instructions, and usage guide

Installation & Setup
Usage Guide
1. Configure the Spindle Order (Sidebar): Keep the default ⁠1–36⁠ sequence, click Shuffle Disks to generate a secret key permutation, or paste a custom 36-number sequence and click Apply Order.
2. Encode a Message (Tab 1 — Sender):
￼ Type your message into Plaintext Message (e.g., ⁠MEETMEATMONTICELLOATSUNRISEWITHPLANS⁠).
￼ Choose a padding letter (default ⁠X⁠) if your message is shorter than 36 letters.
￼ Use the Select Ciphertext Row Offset (1–25) slider to pick which scrambled row to transmit.
￼ Click Lock Cylinder & Send Dispatch to Recipient Tab (or copy the 36-character ciphertext and spindle order to send to a friend).
3. Decipher a Message (Tab 2 — Recipient):
￼ Paste the 36-letter ciphertext into Input 36-Letter Ciphertext Row and ensure the Recipient Spindle Disk Order matches the sender's key.
￼ View the Auto-Detected Readable Plaintext banner at the top, or browse the Full 26-Row Cylinder Scan table where Row +00 is highlighted in blue (ciphertext) and the decoded English row is highlighted in green.
4. Spin the Wheels Manually (Tab 3 — Interactive Cylinder):
￼ Use the global buttons at the top to rotate all 36 wheels up (⁠-1 mod 26⁠), down (⁠+1 mod 26⁠), scramble rotations, or reset offsets to ⁠0⁠.
￼ Use the ⁠▲⁠ and ⁠▼⁠ buttons on any individual wheel in Wheels 1–12, Wheels 13–24, or Wheels 25–36 to step that disk one letter at a time and watch the 26×36 cylinder matrix update live.