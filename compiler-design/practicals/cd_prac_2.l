%{
#include <iostream>
using namespace std;

int vowel_count = 0;
int consonant_count = 0;
%}

%option noyywrap

%%
[aeiouAEIOU]  { ++vowel_count; }
[a-zA-Z]      { ++consonant_count; }
.             { }
\n            { }
%%

int main()
{
    yylex();
    cout << "Vowels: " << vowel_count << '\n';
    cout << "Consonants: " << consonant_count << '\n';
    return 0;
}
