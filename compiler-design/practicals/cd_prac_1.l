%{
#include <iostream>
using namespace std;

int character_count = 0;
int line_count = 0;
bool last_character_was_newline = true;
%}

%option noyywrap

%%
\n      { ++character_count; ++line_count; last_character_was_newline = true; }
.       { ++character_count; last_character_was_newline = false; }
%%

int main()
{
    yylex();
    if (character_count > 0 && !last_character_was_newline)
        ++line_count;

    cout << "Lines: " << line_count << '\n';
    cout << "Characters: " << character_count << '\n';
    return 0;
}
