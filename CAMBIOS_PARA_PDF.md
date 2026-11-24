# Cambios para corregir en los PDFs del análisis EEO

Este documento lista **todo lo que el juego hace distinto o de más** respecto a:

- `EEO_Equipo4_pacman.pdf` (representación, Tabla 1)
- `EEO_Operadores_y_Reglas_Correcion.pdf` (estado inicial, Tabla 2, notación, orden, Tabla 3)

Está ordenado siguiendo las secciones de los PDFs. Cada punto dice **qué dice hoy el PDF** y
**qué debe decir** para que coincida con el código.

---

## 1. Representación del problema

**Hoy dice:** "…sin que lo atrape **el fantasma**…", "…**el fantasma** se asusta…".

**Debe decir:** hay **dos fantasmas**:

| Fantasma | Spawn (valor) | Celda | Inteligencia |
|---|---|---|---|
| 🟢 Verde | 4 (con IA) | (9, 8) | Persigue y huye con reglas inteligentes (22 y 23), más las reglas 11 y 12 |
| 🩷 Rosa | 3 (sin IA) | (9, 10) | Solo camina al azar (regla 24) |

Sugerencia de texto: *"Pac-Man recorre un laberinto y debe comer todos los orbes y súper pastillas
sin que lo atrapen los fantasmas. El fantasma verde tiene inteligencia (embosca a Pac-Man y huye
buscando zonas seguras); el fantasma rosa no tiene inteligencia y se mueve al azar. Cualquiera de los
dos le quita una vida. Al comer una súper pastilla, ambos se asustan…"*

También agregar: *"Los túneles de la fila 7 funcionan como portales: al intentar entrar por un lado,
Pac-Man aparece del otro."*

---

## 2. Valores de la matriz

| Valor | Hoy dice | Debe decir |
|---|---|---|
| 2 | Túnel (se trata como pared) | Túnel / portal: se trata como pared (nadie se queda en él), pero Pac-Man lo cruza con la regla 25 |
| 3 | Spawn del fantasma sin IA | Spawn del fantasma **rosa** (sin IA), (9, 10) |
| 4 | Spawn del fantasma con IA | Spawn del fantasma **verde** (con IA), (9, 8) |

---

## 3. Fórmula (estado)

**Hoy dice:**
```
(EJ, (Fila, Columna, Valor)19x19, (Pf, Pc, Dir, P, T, V), O, S, (Ff, Fc, E), (Pts, Rec))
```

**Debe decir** (un trío `(Ff, Fc, E)` por fantasma):
```
(EJ, (Fila, Columna, Valor)19x19, (Pf, Pc, Dir, P, T, V), O, S,
 (Ffv, Fcv, Ev), (Ffr, Fcr, Er), (Pts, Rec))
```

`v` = verde, `r` = rosa. En el juego, el panel lateral las muestra con esos nombres.

---

## 4. Estado inicial

Cambiar `(Ff, Fc) = (9, 8), E = 0` por:

```
(Ffv, Fcv) = (9, 8), Ev = 0, (Ffr, Fcr) = (9, 10), Er = 0
```

Lo demás queda igual (`EJ = inicio`, mapa inicial, `(Pf, Pc) = (13, 9)`, `Dir = ←`, `P = 0`,
`T = 0`, `V = 3`, `O = 167`, `S = 7`, `Pts = 0`, `Rec = 0`).

> Nota: en el juego, `Rec` se carga de `record.json` si existe (el récord se guarda entre partidas).
> Si no hay archivo, `Rec = 0` como en el PDF.

---

## 5. Tabla 1 · Entidades y variables

Reemplazar la fila **Fantasma** por dos entidades:

| Entidad | Atributo | Variable | Estado (variable) |
|---|---|---|---|
| Fantasma verde (con IA) | Fila | Ffv | 0, 1, 2, …, 18 |
| | Columna | Fcv | 0, 1, 2, …, 18 |
| | Estado | Ev | 0 = normal, 1 = asustado, 2 = comido |
| Fantasma rosa (sin IA) | Fila | Ffr | 0, 1, 2, …, 18 |
| | Columna | Fcr | 0, 1, 2, …, 18 |
| | Estado | Er | 0 = normal, 1 = asustado, 2 = comido |

**Observación (ya estaba así en el PDF original):** el rango de `Pts` y `Rec` dice `0 … 3,690`, pero
3,690 = 167·20 + 7·50 solo cuenta orbes y pastillas. Comer fantasmas suma 200 cada vez y puede pasar
de 3,690. Conviene escribir: *"0, 1, 2, … (3,690 sin contar fantasmas comidos)"*.

---

## 6. Restricciones generales

**Hoy dice:** "Ningún personaje puede entrar a una celda con valor 1 (pared) ni con valor 2 (túnel…)".

**Agregar:** *"Excepción: si Pac-Man intenta entrar a un túnel, no se queda en él; aparece en la celda
de pasillo del otro lado (regla 25). Los fantasmas no usan los túneles."*

---

## 7. Tabla 2 · Reglas que CAMBIAN

Con dos fantasmas, las reglas que hablan de "el fantasma" se aplican **a cada fantasma por separado**
(en el código se llaman, por ejemplo, `salir_casa·verde` y `salir_casa·rosa`). En la tabla se puede
escribir una sola vez con `(Ff, Fc, E)` y una nota: *"se aplica a cada fantasma con sus propias
variables"*.

| # | Operador | Qué cambia |
|---|---|---|
| 1 | iniciar_juego | `(Ffv, Fcv) = (9, 8), Ev = 0, (Ffr, Fcr) = (9, 10), Er = 0` |
| 9 | comer_super | "si E ≠ 2 entonces E = 1" ahora es **para cada fantasma**: `si Ev ≠ 2 entonces Ev = 1; si Er ≠ 2 entonces Er = 1` |
| 10 | salir_casa | Se aplica a cada fantasma. La ruta `siguiente()` ya incluía (9, 10) → (9, 9), que ahora sí usa el rosa |
| 11 | perseguir | **Solo el verde**. Ahora es la regla *general*: se usa cuando `perseguir_inteligente` no aplica (Pac-Man a 4 pasos o menos) |
| 12 | huir | **Solo el verde**. Ahora es la regla *general*: se usa cuando `huir_inteligente` no aplica (Pac-Man a más de 8 pasos) |
| 13 | comer_fantasma | Para cada fantasma. El fantasma comido regresa a **su** spawn: verde a (9, 8), rosa a (9, 10) |
| 14 | perder_vida | La dispara **cualquiera** de los dos fantasmas. Regresa a **ambos** a su spawn: `(Ffv, Fcv) = (9, 8), (Ffr, Fcr) = (9, 10)` |
| 16 | terminar_poder | "si E = 1 entonces E = 0" ahora es **para cada fantasma** |
| 17 | regenerar_fantasma | Se aplica a cada fantasma |

Las reglas 2–8, 15 y 18–21 **no cambian**.

---

## 8. Tabla 2 · Reglas NUEVAS

Mismo formato que la Tabla 2: explicación coloquial y regla formal.

### 22. Perseguir inteligente (fantasma verde)

| Condiciones de aplicabilidad | Operador | Nuevo estado |
|---|---|---|
| Que el fantasma verde esté normal, fuera de la casa y lejos de Pac-Man (más de 4 pasos) | 22. Perseguir inteligente | El fantasma no va a donde está Pac-Man, sino a donde va a estar: predice su posición 4 celdas adelante en su dirección y toma la vecina que más lo acerca a ese punto, para emboscarlo. Cambian: Ffv, Fcv |
| Si EJ = jugando y Ev = 0 y (Ffv, Fcv) ∉ casa y BFS((Ffv, Fcv), (Pf, Pc)) > 4 | perseguir_inteligente | entonces (Ffv, Fcv) = vecina con menor BFS(vecina, predicción(Pf, Pc, Dir, 4)) |

### 23. Huir inteligente (fantasma verde)

| Condiciones de aplicabilidad | Operador | Nuevo estado |
|---|---|---|
| Que el fantasma verde esté asustado, fuera de la casa y cerca de Pac-Man (8 pasos o menos) | 23. Huir inteligente | El fantasma no solo se aleja: de las vecinas que lo alejan de Pac-Man, escoge la que le deja más "territorio" (más celdas a las que llega antes que Pac-Man), para no meterse en un callejón. Cambian: Ffv, Fcv |
| Si EJ = jugando y Ev = 1 y (Ffv, Fcv) ∉ casa y BFS((Ffv, Fcv), (Pf, Pc)) ≤ 8 | huir_inteligente | entonces (Ffv, Fcv) = vecina segura con mayor territorio(vecina) |

### 24. Deambular (fantasma rosa, sin IA)

| Condiciones de aplicabilidad | Operador | Nuevo estado |
|---|---|---|
| Que el fantasma rosa no esté comido y esté fuera de la casa | 24. Deambular | El fantasma se mueve a una celda vecina cualquiera, al azar, sin tomar en cuenta a Pac-Man (ni para perseguirlo ni para huir). Cambian: Ffr, Fcr |
| Si EJ = jugando y Er ≠ 2 y (Ffr, Fcr) ∉ casa | deambular | entonces (Ffr, Fcr) = vecina al azar de vecinas(Ffr, Fcr) |

### 25. Cruzar portal (Pac-Man)

| Condiciones de aplicabilidad | Operador | Nuevo estado |
|---|---|---|
| Que Pac-Man esté junto a un túnel y se mueva hacia él | 25. Cruzar portal | Pac-Man entra por un túnel y aparece del otro lado del laberinto, mirando en la misma dirección. Cambian: Pc, Dir |
| Si EJ = jugando y (Pf, Pc − 1) = (7, 0) | cruzar_portal_izquierda | entonces (Pf, Pc) = (7, 17), Dir = ← |
| Si EJ = jugando y (Pf, Pc + 1) = (7, 18) | cruzar_portal_derecha | entonces (Pf, Pc) = (7, 1), Dir = → |

---

## 9. Notación usada en las reglas (agregar)

- **predicción(Pf, Pc, Dir, k):** la celda a la que llega Pac-Man si avanza hasta `k` celdas en su
  dirección `Dir` sin cruzar paredes, túneles ni la zona de la casa. Si choca antes, se detiene ahí.
  Ejemplo: desde (1, 1) mirando ↓ con k = 4 → (3, 1), porque (4, 1) es pared.
- **territorio(v):** número de celdas a las que el fantasma, partiendo de `v`, llega en **menos**
  pasos BFS que Pac-Man. Es un diagrama de Voronoi sobre los pasillos: mientras más territorio, más
  rutas de escape.
- **vecina segura:** una vecina que no acerca al fantasma a Pac-Man (`BFS(vecina, Pac-Man) ≥ BFS(fantasma, Pac-Man)`).
  Si ninguna lo es (callejón), se consideran todas.
- **vecina al azar:** una de `vecinas(Ff, Fc)` elegida con la misma probabilidad.
- **portales:** (7, 0) → sale en (7, 17); (7, 18) → sale en (7, 1).
- **Parámetros:** umbral de emboscada = 4 pasos, predicción = 4 celdas, radio de peligro = 8 pasos.
- Corregir: *"El fantasma de la fórmula es el que tiene IA (spawn con valor 4, en (9, 8))"* →
  *"El fantasma verde tiene IA (spawn 4, en (9, 8)); el rosa no tiene IA (spawn 3, en (9, 10))."*

Ejemplos para justificar que las reglas son "inteligentes" (los dos están probados en el código):

- **Perseguir:** Pac-Man en (1, 1) mirando ↓ y fantasma en (2, 6). `perseguir` (11) va a (1, 6),
  detrás de él; `perseguir_inteligente` (22) baja a (3, 6) para cortarle el paso en (3, 1).
- **Huir:** Pac-Man en (1, 4) y fantasma asustado en (3, 1). `huir` (12) sube a (2, 1), donde solo
  tiene 4 celdas seguras; `huir_inteligente` (23) va a (3, 2), donde tiene 20.

---

## 10. Operadores evidentes y ocultos

**Evidentes** (los decide el jugador): iniciar, pausar, reanudar, reiniciar, los cuatro movimientos
y **cruzar portal (25)**.

**Ocultos** (los aplica el sistema): comer orbe, comer súper pastilla, salir de casa, perseguir, huir,
comer fantasma, perder vida, reducir y terminar poder, regenerar fantasma, ganar, perder juego,
actualizar récord, **perseguir inteligente (22), huir inteligente (23) y deambular (24)**.

---

## 11. Orden de aplicación en cada ronda

**Hoy dice:** 1) Pac-Man se mueve; 2) colisión; 3) el fantasma se mueve; 4) poder y regeneración;
5) fin de partida.

**Debe decir:**

1. **Pac-Man se mueve** (mover o cruzar portal). Se intenta la dirección que pidió el jugador; si no
   se puede, sigue en su dirección actual `Dir`; si tampoco, se queda quieto.
2. **Colisión:** comer orbe o súper pastilla; luego comer fantasma o perder vida, primero con el verde
   y después con el rosa.
3. **Los fantasmas se mueven**, uno por uno:
   - Verde: salir de casa, perseguir inteligente, perseguir, huir inteligente o huir. Luego se
     vuelve a revisar si choca con Pac-Man.
   - Rosa: salir de casa o deambular. Luego se vuelve a revisar si choca con Pac-Man.
4. **Poder y regeneración:** reducir o terminar poder; regenerar a cada fantasma.
5. **Fin de partida:** ganar, perder juego, actualizar récord.

**Agregar el párrafo de resolución de conflictos:**

> *"En cada paso se dispara como máximo una regla por grupo (por ejemplo, reducir_poder y
> terminar_poder no se aplican en la misma ronda). Cuando dos reglas pueden aplicarse a la vez, gana
> la más específica: perseguir_inteligente tiene las mismas condiciones que perseguir más una (estar
> lejos), así que va primero; lo mismo pasa con huir_inteligente (estar cerca) y huir. La regla general
> solo se aplica si la específica no se cumple."*

> *"Después de mover a cada fantasma se vuelven a revisar las reglas de colisión, porque las reglas
> ocultas se aplican en cuanto se cumplen sus condiciones (Modus Ponens). Así un fantasma no puede
> pasar a través de Pac-Man."*

---

## 12. Tabla 3 · Tabla de estados

La corrida actual **sigue siendo válida** si se lee como el fantasma verde (`Ff, Fc, E` → `Ffv, Fcv, Ev`):
el código la reproduce fila por fila. Para que esté completa:

- Agregar las columnas `Ffr, Fcr, Er` (en esa corrida el rosa se queda en (9, 10) con `Er = 0`,
  porque cada fila aplica un solo operador y ninguno lo mueve).
- Opcional: agregar filas que muestren las reglas nuevas, por ejemplo `salir_casa` del rosa,
  `perseguir_inteligente`, `deambular` y `cruzar_portal`.

---

## 13. Decisiones de implementación (para mencionar si las preguntan)

No contradicen el PDF, pero tampoco están escritas en él:

| Situación | Cómo lo resuelve el juego |
|---|---|
| El jugador no presiona tecla | Pac-Man sigue en su `Dir` hasta chocar |
| Dos fantasmas en la misma celda | Se permite; no chocan entre ellos |
| Empates en BFS | Se desempata por el orden fijo ↑ ↓ ← → (perseguir y huir simples) |
| Duración de una ronda | 170 ms. `T = 8` son 8 rondas, no 8 segundos |
| Récord | Se guarda en `record.json` y se conserva entre ejecuciones |
