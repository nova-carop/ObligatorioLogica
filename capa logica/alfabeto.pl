:- encoding(utf8).

alfabeto(ingles,  [a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z]).
alfabeto(espanol, [a,b,c,d,e,f,g,h,i,j,k,l,m,n,'ñ',o,p,q,r,s,t,u,v,w,x,y,z]).

% Alfabeto de Playfair: 25 letras en MAYUSCULA, sin J (I/J unificadas).
alfabeto(playfair, ['A','B','C','D','E','F','G','H','I','K','L','M',
                    'N','O','P','Q','R','S','T','U','V','W','X','Y','Z']).

idioma_modulo(ingles,  26).
idioma_modulo(espanol, 27).

% Posicion (0-based) de un caracter dentro de un alfabeto dado.
pos_en_alfabeto(Char, Alfabeto, Pos) :-
    nth0(Pos, Alfabeto, Char), !.

% Verdadero si Char pertenece al alfabeto de ese idioma.
char_en_alfabeto(Char, Idioma) :-
    alfabeto(Idioma, Alfa),
    member(Char, Alfa).

% Una letra valida del alfabeto ingles A-Z (en mayuscula).
es_letra(C) :-
    char_code(C, X),
    X >= 0'A, X =< 0'Z.

% Unificacion I/J propia del alfabeto de Playfair
% toda J se convierte en I.
j_a_i('J', 'I') :- !.
j_a_i(C, C).