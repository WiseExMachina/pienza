---
description: Agrega una entrada STAR (Situation/Task/Action/Result) a STAR_stories.md a partir de algo con valor real de historia de entrevista en esta sesion
---

Revisa el trabajo reciente de esta sesion (el ultimo bug diagnosticado, decision con
trade-off, error atrapado antes de salir a producción, o momento de juicio tecnico) y
agregalo como entrada nueva al final de assets_ignored/interview_prep/STAR_stories.md.

Formato de la entrada (igual a las existentes -- primera persona, prosa lista para
decirse en voz alta, no jerga corporativa):

```markdown
## N. <titulo corto>

**Situation:** ...

**Task:** ...

**Action:** ...

**Result:** ...

**Why this story matters:** <que rasgo/habilidad demuestra>
```

Numera la entrada como la siguiente en la secuencia (revisa el numero mas alto ya
existente en el archivo). Actualiza tambien la seccion "Quick reference — one-liners"
al final del archivo con un one-liner nuevo si la historia lo amerita. No reescribas
ni borres entradas anteriores.

Si lo que paso en la sesion no tiene valor real de historia de entrevista (cambio
mecanico, tweak de estilo, propagacion de semicanon), decile al usuario que no
encontraste nada que valga la pena archivar en vez de inventar una historia.

Este comando tambien se dispara proactivamente (sin que el usuario tenga que
invocarlo): cuando un pedazo de trabajo en la sesion tenga valor real de historia
(bug con diagnostico genuino, decision defendible, error atrapado antes de salir,
juicio tecnico incluyendo saber cuando NO seguir optimizando), agregalo sin esperar
a que el usuario escriba /star -- y avisale brevemente que lo hiciste.
