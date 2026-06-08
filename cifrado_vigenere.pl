:- encoding(utf8).
:- consult(alfabeto).

extender_clave(_, 0, []) :- !.
extender_clave(Clave, Largo, [LetraClave|Resto]) :-
    Largo > 0,
    length(Clave, LongClave),
    Indice is (Largo - 1) mod LongClave,
    nth0(Indice, Clave, LetraClave),
    LargoMenos1 is Largo - 1,
    extender_clave(Clave, LargoMenos1, Resto).

clave_extendida(Clave, Largo, ClaveExtendida) :-
    extender_clave(Clave, Largo, ClaveAlReves),
    reverse(ClaveAlReves, ClaveExtendida).

cifrar_char(Char, LetraClave, Idioma, CharCifrado) :-
    alfabeto(Idioma, Alfa),
    idioma_modulo(Idioma, Modulo),
    pos_en_alfabeto(Char, Alfa, PosChar),
    pos_en_alfabeto(LetraClave, Alfa, PosClave), !,
    NuevaPos is (PosChar + PosClave) mod Modulo,
    nth0(NuevaPos, Alfa, CharCifrado).
cifrar_char(Char, _, _, Char).

descifrar_char(Char, LetraClave, Idioma, CharOriginal) :-
    alfabeto(Idioma, Alfa),
    idioma_modulo(Idioma, Modulo),
    pos_en_alfabeto(Char, Alfa, PosChar),
    pos_en_alfabeto(LetraClave, Alfa, PosClave), !,
    NuevaPos is ((PosChar - PosClave) mod Modulo + Modulo) mod Modulo,
    nth0(NuevaPos, Alfa, CharOriginal).
descifrar_char(Char, _, _, Char).

cifrar_lista([], _, _, []).
cifrar_lista([H|T], [K|Ks], Idioma, [HC|TC]) :-
    cifrar_char(H, K, Idioma, HC),
    cifrar_lista(T, Ks, Idioma, TC).

descifrar_lista([], _, _, []).
descifrar_lista([H|T], [K|Ks], Idioma, [HC|TC]) :-
    descifrar_char(H, K, Idioma, HC),
    descifrar_lista(T, Ks, Idioma, TC).

cifrar(Mensaje, Clave, Idioma, Cifrado) :-
    downcase_atom(Mensaje, M), atom_chars(M, ListaMensaje),
    downcase_atom(Clave, C),   atom_chars(C, ListaClave),
    length(ListaMensaje, Largo),
    clave_extendida(ListaClave, Largo, ClaveExtendida),
    cifrar_lista(ListaMensaje, ClaveExtendida, Idioma, ListaCifrada),
    atomic_list_concat(ListaCifrada, Cifrado).

descifrar(Cifrado, Clave, Idioma, Mensaje) :-
    downcase_atom(Cifrado, C), atom_chars(C, ListaCifrada),
    downcase_atom(Clave, K),   atom_chars(K, ListaClave),
    length(ListaCifrada, Largo),
    clave_extendida(ListaClave, Largo, ClaveExtendida),
    descifrar_lista(ListaCifrada, ClaveExtendida, Idioma, ListaMensaje),
    atomic_list_concat(ListaMensaje, Mensaje).