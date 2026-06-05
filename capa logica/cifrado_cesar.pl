% ============================================================
%  CIFRADO CÉSAR
% ============================================================

:- encoding(utf8).
:- consult(alfabeto).

% Desplazamiento fijo para la demo educativa
desp_fijo(3).


% ------------------------------------------------------------
% desplazar(+Pos, +Desp, +Modulo, -NuevaPos)
% ------------------------------------------------------------

desplazar(Pos, Desp, Modulo, NuevaPos) :-
    NuevaPos is ((Pos + Desp) mod Modulo + Modulo) mod Modulo.


% ------------------------------------------------------------
% cifrar_char(+Char, +Desp, +Idioma, -CharCifrado)
% ------------------------------------------------------------

cifrar_char(Char, Desp, Idioma, CharCifrado) :-
    alfabeto(Idioma, Alfa),
    idioma_modulo(Idioma, Modulo),
    pos_en_alfabeto(Char, Alfa, Pos), !,
    desplazar(Pos, Desp, Modulo, NuevaPos),
    nth0(NuevaPos, Alfa, CharCifrado).

cifrar_char(Char, _, _, Char).  % espacios y símbolos: sin cambio


% ------------------------------------------------------------
% cifrar_lista(+Lista, +Desp, +Idioma, -Resultado)
% ------------------------------------------------------------

cifrar_lista([], _, _, []).

cifrar_lista([H|T], Desp, Idioma, [HC|TC]) :-
    cifrar_char(H, Desp, Idioma, HC),
    cifrar_lista(T, Desp, Idioma, TC).


% ============================================================
%  MENÚ DE PRUEBA  (será reemplazado por frontend Python)
% ============================================================

menu :-
    nl,
    write('=== CIFRADO CÉSAR ==='), nl,
    write('1. Cifrar mensaje'), nl,
    write('2. Descifrar mensaje'), nl,
    write('3. Salir'), nl,
    write('Opcion: '),
    read(Opcion),
    manejar_opcion(Opcion).


% --- Leer idioma ---
leer_idioma(Idioma) :-
    write('Idioma (espanol/ingles): '),
    read(Idioma),
    ( idioma_modulo(Idioma, _) -> true
    ; write('Idioma invalido. Usa espanol o ingles.'), nl, leer_idioma(Idioma)
    ).


% --- Leer desplazamiento ---
leer_desplazamiento(Desp) :-
    nl,
    write('Tipo de desplazamiento:'), nl,
    write('  1. Fijo (3) - para ver como funciona el cifrado'), nl,
    write('  2. Personalizado'), nl,
    write('Opcion: '),
    read(TipoDesp),
    resolver_desp(TipoDesp, Desp).

resolver_desp(1, Desp) :- !,
    desp_fijo(Desp),
    write('Desplazamiento fijo: '), write(Desp), nl.

resolver_desp(2, Desp) :- !,
    write('Ingrese el desplazamiento: '),
    read(Desp),
    ( integer(Desp) -> true
    ; write('Debe ser un numero entero.'), nl, fail
    ).

resolver_desp(_, Desp) :-
    write('Opcion invalida.'), nl,
    leer_desplazamiento(Desp).


% --- Convierte átomo a lista de chars en minúsculas ---
leer_mensaje(Lista) :-
    write('Mensaje (ej: hola): '),
    read(Atom),
    downcase_atom(Atom, Lower),
    atom_chars(Lower, Lista).

% --- Convierte lista de chars a átomo para mostrar ---
mostrar_resultado(Lista) :-
    atomic_list_concat(Lista, Resultado),
    write(Resultado).


% --- Opción 1: Cifrar ---
manejar_opcion(1) :-
    write('--- CIFRAR ---'), nl,
    leer_mensaje(Lista),
    leer_idioma(Idioma),
    leer_desplazamiento(Desp),
    cifrar_lista(Lista, Desp, Idioma, Cifrado),
    nl, write('Resultado: '), mostrar_resultado(Cifrado), nl,
    menu.


% --- Opción 2: Descifrar ---
manejar_opcion(2) :-
    write('--- DESCIFRAR ---'), nl,
    leer_mensaje(Lista),
    leer_idioma(Idioma),
    leer_desplazamiento(Desp),
    DesNeg is -Desp,
    cifrar_lista(Lista, DesNeg, Idioma, Original),
    nl, write('Resultado: '), mostrar_resultado(Original), nl,
    menu.


% --- Opción 3: Salir ---
manejar_opcion(3) :-
    write('Hasta luego.'), nl.


% --- Opción inválida ---
manejar_opcion(_) :-
    write('Opcion invalida.'), nl,
    menu.