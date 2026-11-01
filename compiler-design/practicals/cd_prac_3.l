%{
#include <iostream>
using namespace std;
%}

%option noyywrap

%%
[a-z]         { cout.put('a' + (yytext[0] - 'a' + 3) % 26); }
[A-Z]         { cout.put('A' + (yytext[0] - 'A' + 3) % 26); }
.             { cout << yytext[0]; }
\n            { cout << '\n'; }
%%

int main()
{
    yylex();
    return 0;
}
