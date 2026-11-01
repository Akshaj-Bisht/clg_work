
%{
#include <stdio.h>
#include <string.h>
%}

%%
.|\n    { }
%%

int main()
{
    char str[] = "abcd";
    int i;

    for (i = strlen(str); i > 0; i--)
    {
        printf("%.*s\n", i, str);
    }

    return 0;
}

int yywrap()
{
    return 1;
}
