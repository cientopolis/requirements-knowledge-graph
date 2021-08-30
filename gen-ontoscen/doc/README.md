# Casos de análisis para el procesamiento de los episodios

## Casos

1. En el episodio ep1 aparece actor1 como sujeto de ep1 y actor1 es Actor en el grafo G o no es Recurso en G. 
    1. Por lo tanto actor1 es de tipo Actor por su rol en el episodio.
    2. Insertar o usar individuo de actor1.
    3. Agregar al G la tripleta {ep1, hasActor, actor1}

2. En el episodio ep1 aparece actor1 como sujeto de ep1 y actor1 es Recurso en G.
    1. Por lo tanto actor1 es de tipo Actor por su rol en el episodio.
    2.  Insertar o usar individuo de actor1.
    3. Agregar al G la tripleta {ep1, hasActor, actor1}
    4. DETECTAR INCONSISTENCIA: un elemento de tipo Actor es en el grafo también Recurso.

3. En el episodio ep1 aparece r1 como objeto en el predicado del ep1 y r1 es un Resource en el grafo G o no es Actor en G. 
    1. Por lo tanto r1 es de tipo Resource por su rol en el episodio ep1.
    2. Insertar o usar individuo de r1.
    3. Agregar al grafo G la tripleta {ep1 hasResource r1}.

4. En el episodio ep1 aparece r1 como objeto en el predicado del ep1 y r1 es un Actor en G.
    1. Por lo tanto r1 es un Resource por su rol en el episodio. 
    2. Insertar o usar individuo r1. 
    3. Agregar al grafo G la tripleta {ep1 hasResource r1}.
    4. DETECTAR INCONSISTENCIA: un elemento de tipo Resource en el grafo también es Actor.



5. Si aparece un of, queda el más completo



6. Caso with: se detecta como recurso y se agrega como recurso del ep, same caso 3



7. Caso adjetivo + actor|recurso.