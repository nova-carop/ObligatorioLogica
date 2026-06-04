
:- consult(alfabeto).  

desplazar(Pos, Desp, Modulo, NuevaPos) :-
    NuevaPos is ((Pos + Desp) mod Modulo + Modulo) mod Modulo.


cifrar_char(Char, Desp, Modulo, CharCifrado) :-
    alfabeto(Modulo, Alfa),
    pos_en_alfabeto(Char, Alfa, Pos), !,   % carácter encontrado
    desplazar(Pos, Desp, Modulo, NuevaPos),
    nth0(NuevaPos, Alfa, CharCifrado).

cifrar_char(Char, _Desp, _Modulo, Char).   % carácter no alfabético: sin cambio


cifrar_lista([], _Desp, _Modulo, []).

cifrar_lista([H|T], Desp, Modulo, [HC|TC]) :-
    cifrar_char(H, Desp, Modulo, HC),
    cifrar_lista(T, Desp, Modulo, TC).


cesar(Texto, Desp, Resultado) :-
    ( member(ñ, Texto) -> Modulo = 27 ; Modulo = 26 ),
    cifrar_lista(Texto, Desp, Modulo, Resultado).

%    Desp > 0  → cifra
%    Desp < 0  → descifra  (o usar -Desp para descifrar)
%    El módulo se elige automáticamente según si la lista
%    contiene la letra ñ (módulo 27) o no (módulo 26).



%INFERFAZ DE PRUEBA

leer_entrada(Texto, Desp, Modulo) :-
    write('Ingrese el mensaje como lista de átomos (ej: [h,o,l,a]): '),
    read(Texto),
    write('Ingrese el desplazamiento (positivo=cifrar, negativo=descifrar): '),
    read(Desp),
    write('Ingrese el módulo (26=inglés, 27=español): '),
    read(Modulo).




menu :-
    nl,
    write('=== CIFRADO CÉSAR ==='), nl,
    write('1. Cifrar mensaje'), nl,
    write('2. Descifrar mensaje'), nl,
    write('3. Salir'), nl,
    write('Opción: '),
    read(Opcion),
    manejar_opcion(Opcion).

manejar_opcion(1) :-
    write('--- CIFRAR ---'), nl,
    write('Mensaje como lista (ej: [h,o,l,a]): '), read(Texto),
    write('Desplazamiento: '), read(Desp),
    write('Módulo (26/27): '), read(Modulo),
    cifrar_lista(Texto, Desp, Modulo, Cifrado),
    write('Resultado: '), write(Cifrado), nl,
    menu.

manejar_opcion(2) :-
    write('--- DESCIFRAR ---'), nl,
    write('Mensaje cifrado como lista: '), read(Texto),
    write('Desplazamiento original: '), read(Desp),
    write('Módulo (26/27): '), read(Modulo),
    DesNeg is -Desp,
    cifrar_lista(Texto, DesNeg, Modulo, Original),
    write('Resultado: '), write(Original), nl,
    menu.

manejar_opcion(3) :-
    write('¡Hasta luego!'), nl.

manejar_opcion(_) :-
    write('Opción inválida.'), nl,
    menu.


