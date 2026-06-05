
:- encoding(utf8).

alfabeto(ingles,  [a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z]).
alfabeto(espanol, [a,b,c,d,e,f,g,h,i,j,k,l,m,n,'ñ',o,p,q,r,s,t,u,v,w,x,y,z]).

idioma_modulo(ingles,  26).
idioma_modulo(espanol, 27).

pos_en_alfabeto(Char, Alfabeto, Pos) :-
    nth0(Pos, Alfabeto, Char), !.

char_en_alfabeto(Char, Idioma) :-
    alfabeto(Idioma, Alfa),
    member(Char, Alfa).