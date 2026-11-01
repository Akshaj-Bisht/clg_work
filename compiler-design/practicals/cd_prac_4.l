%{
#include <iostream>
#include <string>
using namespace std;

string longest_word;
int longest_length = 0;
%}

%option noyywrap

%%
[A-Za-z]+     {
                  if (yyleng > longest_length) {
                      longest_length = yyleng;
                      longest_word = yytext;
                  }
              }
.             { }
\n            { }
%%

int main()
{
    yylex();
    if (longest_word.empty())
        cout << "No word found.\n";
    else
        cout << "Longest word: " << longest_word << '\n';
    return 0;
}
