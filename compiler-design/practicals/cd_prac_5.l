%{
#include <iostream>
using namespace std;
%}

%option noyywrap
%x COMMENT

%%
"//"[^\n]* {
    cout << "Comment: " << yytext << '\n';
}

"/*" {
    cout << "Comment: " << yytext;
    BEGIN(COMMENT);
}

<COMMENT>"*/" {
    cout << yytext << '\n';
    BEGIN(INITIAL);
}

<COMMENT>\n {
    cout << '\n';
}

<COMMENT>. {
    cout << yytext[0];
}

(if|else|while|for|do|switch) {
    cout << "Keyword: " << yytext << '\n';
}

(case|break|continue|return) {
    cout << "Keyword: " << yytext << '\n';
}

(int|float|double|char|void|bool|const) {
    cout << "Keyword: " << yytext << '\n';
}

[0-9]+\.[0-9]+([eE][+-]?[0-9]+)? {
    cout << "Float: " << yytext << '\n';
}

[0-9]+ {
    cout << "Integer: " << yytext << '\n';
}

[A-Za-z_][A-Za-z0-9_]* {
    cout << "Identifier: " << yytext << '\n';
}

("=="|"!="|"<="|">="|"++"|"--") {
    cout << "Operator: " << yytext << '\n';
}

("&&"|"||"|"+="|"-="|"*="|"/="|"%="|"->") {
    cout << "Operator: " << yytext << '\n';
}

[+*/%=<>!&|^~-] {
    cout << "Operator: " << yytext << '\n';
}

[ \t\r\n]+ {
    /* Ignore whitespace between tokens. */
}

. {
    cout << "Symbol: " << yytext << '\n';
}
%%

int main()
{
    yylex();
    return 0;
}
