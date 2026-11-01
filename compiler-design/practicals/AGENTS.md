# Practical Implementation Notes

## Goal
Create simple Lex programs with C++ actions for Compiler Design practicals 1–6, based on `COMPILER DESIGN_guidelines.pdf`. Practical 7 already exists as `cd_prac_7.l` and is left unchanged.

## Conventions
- Each practical is a standalone `.l` file.
- Lex-generated source is compiled with `g++`; actions use C++ streams.
- Lex rules perform scanning; C++ standard streams and strings handle output and state.
- Update this file whenever a practical is added or revised.

## Progress
- [x] Practical 1 — Count lines and characters (`cd_prac_1.l`)
- [x] Practical 2 — Count vowels and consonants (`cd_prac_2.l`)
- [x] Practical 3 — Caesar cipher with shift of three (`cd_prac_3.l`)
- [x] Practical 4 — Find the longest alphabetic word (`cd_prac_4.l`)
- [x] Practical 5 — Classify keywords, numbers, identifiers, operators, and comments (`cd_prac_5.l`)
- [x] Practical 6 — Count words, characters, blanks, and lines (`cd_prac_6.l`)

## Validation
- Built all six programs with Flex and `g++ -std=c++17 -Wall -Wextra -pedantic`.
- Smoke-checked each program with representative input.
- `README.md` contains build/run instructions and each program's behavior.
- Simplified counter variables to ordinary `int` globals and added `using namespace std;` as requested; rebuilt all six successfully.
- Clarified that practical 6 can scan either C or C++ source text.
- Rebuilt and smoke-checked practicals 1–7; each executable ran successfully. Practical 7's generated scanner emits Flex's unused `yyunput` warning, but compiles and produces the expected output.
- Added `prac5_program.cpp`, `prac6_program.cpp`, and `prac1_input.txt` as ready-to-use sample inputs.
- Added `Compiler Design Practicals.md` with the practical headings, full source code, build/run commands, and sample output for practicals 1–7.
- Reordered the practical document so each syntax-highlighted Lex source block appears before its sample output.
- Changed code fences to Obsidian-supported `cpp`/`c` tags, labeled captured output as `Output`, and embedded the contents of the practical 1, 5, and 6 input files.
- Removed unused `nounput` and `noinput` options, kept `noyywrap`, simplified practical 3's character output and practical 4's longest-word comparison, and synchronized the Markdown source. Rebuilt all seven and checked practicals 2–4.
- Reformatted practical 5 rules and actions onto compact lines for Obsidian readability; rebuilt and confirmed its output is unchanged.
