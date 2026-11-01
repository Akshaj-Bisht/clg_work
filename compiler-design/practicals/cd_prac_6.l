%{
#include <iostream>
using namespace std;

int word_count = 0;
int character_count = 0;
int blank_count = 0;
int line_count = 0;
bool last_character_was_newline = true;
%}

%option noyywrap

%%
[^ \t\r\n]+   { ++word_count; character_count += yyleng; last_character_was_newline = false; }
[ \t\r]       { ++character_count; ++blank_count; last_character_was_newline = false; }
\n            { ++character_count; ++line_count; last_character_was_newline = true; }
%%

int main()
{
    yylex();
    if (character_count > 0 && !last_character_was_newline)
        ++line_count;

    cout << "Words: " << word_count << '\n';
    cout << "Characters: " << character_count << '\n';
    cout << "Blank spaces: " << blank_count << '\n';
    cout << "Lines: " << line_count << '\n';
    return 0;
}
