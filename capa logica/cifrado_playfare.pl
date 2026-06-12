% se necesita una clave,una matriz 5x5 y el texto a cifrar
%se puede cifrar con y sin espacios(a eleccion del usuario)
%I/J unificados para que quede 5x5 la matriz
%Las letras repetidas se ponen una vez
%Se agrega una X entre letras repetidas o al final si el mensaje tiene longitud impar.
:- encoding(utf8).

:- encoding(utf8).


%Pasa a mayúsculas, descarta lo que no sea A-Z y unifica J->I.


limpiar(Texto, Limpio) :-
    upcase_atom(Texto, Mayus),
    atom_chars(Mayus, Chars),
    include(es_letra, Chars, Letras),
    maplist(j_a_i, Letras, Limpio).

% Solo letras del alfabeto inglés A-Z (descarta espacios, tildes, signos).
es_letra(C) :-
    char_code(C, X),
    X >= 0'A, X =< 0'Z.

% Unificación I/J: toda J se convierte en I.
j_a_i('J', 'I') :- !.
j_a_i(C,   C).



construir_matriz(Clave, Matriz) :-
    limpiar(Clave, ClaveLimpia),
    atom_chars('ABCDEFGHIKLMNOPQRSTUVWXYZ', Alfabeto),   
    append(ClaveLimpia, Alfabeto, Todo),
    sin_repetidos(Todo, Matriz).

% Elimina repetidos conservando la primera aparición.
sin_repetidos([], []).
sin_repetidos([X|Xs], [X|Ys]) :-
    exclude(==(X), Xs, Resto),
    sin_repetidos(Resto, Ys).


formar_pares([], []).
formar_pares([X], [[X,R]]) :- !,
    relleno(X, R).

% Dos letras iguales seguidas -> separar con relleno.
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
    ;                                              % rectángulo -> cambio de columnas
        letra_en(Matriz, FA, CB, RA),
        letra_en(Matriz, FB, CA, RB)
    ).


desplazar(I, Dir, I2) :-
    I2 is (I + Dir + 5) mod 5.



% PREDICADOS PRINCIPALES

%Cifrar: salida sin espacios 
cifrar(Clave, Texto, Cifrado) :-
    procesar(Clave, Texto, 1, Pares),
    flatten(Pares, Chars),
    atom_chars(Cifrado, Chars).

%Cifrar: salida con espacios-
cifrar_con_espacios(Clave, Texto, Cifrado) :-
    procesar(Clave, Texto, 1, Pares),
    pares_a_texto(Pares, Cifrado).

%Descifrar (a partir del texto cifrado continuo)
descifrar(Clave, Cifrado, Texto) :-
    procesar(Clave, Cifrado, -1, Pares),
    flatten(Pares, Chars),
    atom_chars(Texto, Chars).

% Núcleo común: limpia, arma pares y los transforma.
procesar(Clave, Texto, Dir, ParesResultado) :-
    construir_matriz(Clave, Matriz),
    limpiar(Texto, Limpio),
    formar_pares(Limpio, Pares),
    maplist(transformar_par(Matriz, Dir), Pares, ParesResultado).

% Convierte [[A,B],[C,D]] en el átomo 'AB CD'.
pares_a_texto(Pares, Texto) :-
    maplist(par_a_atomo, Pares, Atomos),
    atomic_list_concat(Atomos, ' ', Texto).

par_a_atomo([A,B], AB) :-
    atom_chars(AB, [A,B]).


% ------------------------------------------------------------
%  7. UTILIDAD: mostrar la matriz por pantalla
% ------------------------------------------------------------

mostrar_matriz(Clave) :-
    construir_matriz(Clave, Matriz),
    format("Matriz 5x5 para la clave \"~w\":~n", [Clave]),
    imprimir_filas(Matriz).

imprimir_filas([]).
imprimir_filas([A,B,C,D,E|Resto]) :-
    format("  ~w ~w ~w ~w ~w~n", [A,B,C,D,E]),
    imprimir_filas(Resto).


% ============================================================
%  EJEMPLOS DE USO (cárgalos con: ?- swipl playfair.pl )
% ------------------------------------------------------------
%  ?- mostrar_matriz('PLAYFAIR EXAMPLE').
%  ?- cifrar('PLAYFAIR EXAMPLE', 'HIDE THE GOLD', C).
%       C = 'BMODZBXDNABE...'
%  ?- cifrar_con_espacios('CLAVE', 'mensaje secreto', C).
%  ?- descifrar('PLAYFAIR EXAMPLE', 'BMODZBXDNABE', T).
% ============================================================


% ============================================================
%  8. MENÚ DE PRUEBA INTERACTIVO
% ------------------------------------------------------------
%  Para usarlo en VS Code:
%    1) Abre la terminal y ejecuta:   swipl playfair.pl
%    2) En el prompt ?-  escribe:     menu.
%  (o descomenta la línea de initialization de más abajo para
%   que el menú arranque solo al cargar el archivo).
% ============================================================

% :- initialization(menu).   % <- descomenta para arranque automático

menu :-
    nl,
    writeln('==================================================='),
    writeln('            CIFRADO PLAYFAIR - MENU'),
    writeln('==================================================='),
    writeln('  1. Mostrar la matriz 5x5 de una clave'),
    writeln('  2. Cifrar texto (salida continua, SIN espacios)'),
    writeln('  3. Cifrar texto (en pares, CON espacios)'),
    writeln('  4. Descifrar texto'),
    writeln('  5. Salir'),
    writeln('---------------------------------------------------'),
    write('  Elige una opcion (1-5): '),
    leer_atomo(Opcion),
    procesar_opcion(Opcion).

procesar_opcion('1') :- !,
    pedir('Clave', Clave),
    nl, mostrar_matriz(Clave),
    menu.

procesar_opcion('2') :- !,
    pedir('Clave', Clave),
    pedir('Texto a cifrar', Texto),
    cifrar(Clave, Texto, C),
    format("~n  >> Cifrado: ~w~n", [C]),
    menu.

procesar_opcion('3') :- !,
    pedir('Clave', Clave),
    pedir('Texto a cifrar', Texto),
    cifrar_con_espacios(Clave, Texto, C),
    format("~n  >> Cifrado: ~w~n", [C]),
    menu.

procesar_opcion('4') :- !,
    pedir('Clave', Clave),
    pedir('Texto cifrado', Texto),
    descifrar(Clave, Texto, T),
    format("~n  >> Descifrado: ~w~n", [T]),
    menu.

procesar_opcion('5') :- !,
    writeln(''), writeln('  Hasta luego!'), nl.

procesar_opcion(_) :-
    writeln(''), writeln('  Opcion invalida, intenta de nuevo.'),
    menu.

% --- Lectura de entrada del usuario como átomo ---
pedir(Etiqueta, Valor) :-
    format("  ~w: ", [Etiqueta]),
    leer_atomo(Valor).

leer_atomo(Atomo) :-
    read_line_to_string(user_input, Linea),
    ( Linea == end_of_file -> Atomo = '5' ; atom_string(Atomo, Linea) ).
% ============================================================