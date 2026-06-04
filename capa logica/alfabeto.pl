
alfabeto(26, [a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z]).
alfabeto(27, [a,b,c,d,e,f,g,h,i,j,k,l,m,n,ñ,o,p,q,r,s,t,u,v,w,x,y,z]).

modulo_valido(26).
modulo_valido(27).


pos_en_alfabeto(Char, Alfabeto, Pos) :-
    nth0(Pos, Alfabeto, Char), !. %El corte evita buscar posiciones duplicadas.


char_en_alfabeto(Char, Modulo) :-   %Verifica si un carácter pertenece al alfabeto del módulo.
    alfabeto(Modulo, Alfa),
    member(Char, Alfa).