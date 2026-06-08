letra_num(Letra, Numero) :- char_code(Letra, Codigo) , Numero is Codigo - 65.

num_letra(Numero, Letra) :- Codigo is Numero + 65 , char_code(Letra, Codigo).

extender_clave(_, 0, []) :- !.
extender_clave(Clave, N, [K|Resto]) :-
    N > 0,
    length(Clave, Len),
    Idx is (N - 1) mod Len,
    nth0(Idx, Clave, K),
    N1 is N - 1,
    extender_clave(Clave, N1, Resto).

cifrar_letras([], [], []).
cifrar_letras([M|Ms], [K|Ks], [C|Cs]) :-
    letra_num(M, NM),
    letra_num(K, NK),
    NC is (NM + NK) mod 26,
    num_letra(NC, C),
    cifrar_letras(Ms, Ks, Cs).
  
descifrar_letras([], [], []).
descifrar_letras([C|Cs], [K|Ks], [M|Ms]) :-
    letra_num(C, NC),
    letra_num(K, NK),
    NM is (NC - NK + 26) mod 26,
    num_letra(NM, M),
    descifrar_letras(Cs, Ks, Ms).

  %Predicado Principal
  cifrar(Mensaje, Clave, Cifrado) :-
    upcase_atom(Mensaje, MU), atom_chars(MU, LM),
    upcase_atom(Clave, CU),   atom_chars(CU, LC),
    length(LM, Largo),
    clave_extendida(LC, Largo, LCext),
    cifrar_letras(LM, LCext, LCif),
    atom_chars(Cifrado, LCif).