# Compiler Design Practicals 1–7

These standalone Lex programs use C++ actions. The complete practical write-up, including source and sample output, is in [Compiler Design Practicals.md](Compiler%20Design%20Practicals.md). Practical 7 is retained as provided.

For printing, use the formatted [Compiler Design Practicals PDF](Compiler%20Design%20Practicals.pdf). It includes syntax-highlighted source listings and line numbers. Regenerate it after editing the Markdown with `python scripts/render_compiler_practicals_pdf.py` from the repository root.

## Build and run

Run these commands from this directory. Replace `N` with the practical number:

```sh
flex -o lex.yy.cpp cd_prac_N.l
g++ -std=c++17 lex.yy.cpp -o practical_N
./practical_N < input.txt
```

Practical 3 prints a Caesar cipher result; practical 5 prints token classifications. The other programs print their results after reading input. Practical 6 can scan C or C++ source text, for example:

```sh
./practical_6 < prac6_program.cpp
```

## Source files

- `cd_prac_1.l` counts lines and characters.
- `cd_prac_2.l` counts vowels and consonants.
- `cd_prac_3.l` applies a Caesar shift of three.
- `cd_prac_4.l` finds the longest alphabetic word.
- `cd_prac_5.l` classifies keywords, numbers, identifiers, operators, and comments.
- `cd_prac_6.l` counts words, characters, blanks, and lines.
- `cd_prac_7.l` contains the existing seventh practical.
