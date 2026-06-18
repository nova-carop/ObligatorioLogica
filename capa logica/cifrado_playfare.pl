% se necesita una clave, una matriz 5x5 y el texto a cifrar
% se puede cifrar con y sin espacios (a eleccion del usuario)
% I/J unificados para que quede 5x5 la matriz
% Las letras repetidas se ponen una vez
% Se agrega una X entre letras repetidas o al final si el mensaje tiene longitud impar.
:- encoding(utf8).
:- consult('alfabeto').


% Pasa a mayusculas, descarta lo que no sea A-Z y unifica J->I.
limpiar(Texto, Limpio) :-
    upcase_atom(Texto, Mayus),
    atom_chars(Mayus, Chars),
    include(es_letra, Chars, Letras),
    maplist(j_a_i, Letras, Limpio).


construir_matriz(Clave, Matriz) :-
    limpiar(Clave, ClaveLimpia),
    alfabeto(playfair, Alfabeto),       
    append(ClaveLimpia, Alfabeto, Todo),
    sin_repetidos(Todo, Matriz).

% Elimina repetidos conservando la primera aparicion.
sin_repetidos([], []).
sin_repetidos([X|Xs], [X|Ys]) :-
    exclude(==(X), Xs, Resto),
    sin_repetidos(Resto, Ys).


formar_pares([], []).
formar_pares([X], [[X,R]]) :- !,
    relleno(X, R).

% Dos letras iguales seguidas se separan con relleno.
formar_pares([X,X|Resto], [[X,R]|Pares]) :- !,
    relleno(X, R),
    formar_pares([X|Resto], Pares).

% Caso normal: par de letras distintas.
formar_pares([X,Y|Resto], [[X,Y]|Pares]) :-
    formar_pares(Resto, Pares).

% Letra de relleno: 'X', salvo cuando la letra ya es 'X' (usa 'Q').
relleno('X', 'Q') :- !.
relleno(_,   'X').


posicion(Matriz, Letra, Fila, Col) :-
    nth0(Indice, Matriz, Letra), !,
    Fila is Indice // 5,
    Col  is Indice mod 5.

letra_en(Matriz, Fila, Col, Letra) :-
    Indice is Fila * 5 + Col,
    nth0(Indice, Matriz, Letra).


transformar_par(Matriz, Dir, [A,B], [RA,RB]) :-
    posicion(Matriz, A, FA, CA),
    posicion(Matriz, B, FB, CB),
    (   FA =:= FB                                  % misma fila
    ->  desplazar(CA, Dir, CA2), desplazar(CB, Dir, CB2),
        letra_en(Matriz, FA, CA2, RA),
        letra_en(Matriz, FB, CB2, RB)
    ;   CA =:= CB                                  % misma columna
    ->  desplazar(FA, Dir, FA2), desplazar(FB, Dir, FB2),
        letra_en(Matriz, FA2, CA, RA),
        letra_en(Matriz, FB2, CB, RB)
    ;                                              % rectangulo -> cambio de columnas
        letra_en(Matriz, FA, CB, RA),
        letra_en(Matriz, FB, CA, RB)
    ).

desplazar(I, Dir, I2) :-
    I2 is (I + Dir + 5) mod 5.

% PREDICADOS PRINCIPALES

% Cifrar: salida sin espacios
cifrar(Clave, Texto, Cifrado) :-
    procesar(Clave, Texto, 1, Pares),
    flatten(Pares, Chars),
    atom_chars(Cifrado, Chars).

% Cifrar: salida con espacios
cifrar_con_espacios(Clave, Texto, Cifrado) :-
    procesar(Clave, Texto, 1, Pares),
    pares_a_texto(Pares, Cifrado).

% Descifrar (a partir del texto cifrado continuo)
descifrar(Clave, Cifrado, Texto) :-
    procesar(Clave, Cifrado, -1, Pares),
    flatten(Pares, Chars),
    atom_chars(Texto, Chars).

procesar(Clave, Texto, Dir, ParesResultado) :-
    construir_matriz(Clave, Matriz),
    limpiar(Texto, Limpio),
    formar_pares(Limpio, Pares),
    maplist(transformar_par(Matriz, Dir), Pares, ParesResultado).

pares_a_texto(Pares, Texto) :-
    maplist(par_a_atomo, Pares, Atomos),
    atomic_list_concat(Atomos, ' ', Texto).

par_a_atomo([A,B], AB) :-
    atom_chars(AB, [A,B]).


