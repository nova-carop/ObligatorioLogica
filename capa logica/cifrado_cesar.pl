:- encoding(utf8).
:- consult(alfabeto).

% Desplazamiento fijo para la demo educativa
desp_fijo(3).


desplazar(Pos, Desp, Modulo, NuevaPos) :-
    NuevaPos is ((Pos + Desp) mod Modulo + Modulo) mod Modulo.


cifrar_char(Char, Desp, Idioma, CharCifrado) :-
    alfabeto(Idioma, Alfa),
    idioma_modulo(Idioma, Modulo),
    pos_en_alfabeto(Char, Alfa, Pos), !,
    desplazar(Pos, Desp, Modulo, NuevaPos),
    nth0(NuevaPos, Alfa, CharCifrado).

cifrar_char(Char, _, _, Char).  % espacios y símbolos: sin cambio



cifrar_lista([], _, _, []).

cifrar_lista([H|T], Desp, Idioma, [HC|TC]) :-
    cifrar_char(H, Desp, Idioma, HC),
    cifrar_lista(T, Desp, Idioma, TC).

% --- DESCIFRADO ---
descifrar_lista(Lista, Desp, Idioma, Descifrado) :-
    DespNegativo is -Desp,
    cifrar_lista(Lista, DespNegativo, Idioma, Descifrado).



