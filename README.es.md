# Sovereign Memory Protocol (SMP)

*🇬🇧 [English](README.md) · 🇩🇪 [Deutsch](README.de.md) · 🇪🇸 **Español** · 🇷🇺 [Русский](README.ru.md)*

*Un protocolo para memoria de IA atestiguada y autoalojada — memoria a largo plazo para agentes LLM que mantiene a una IA como la misma mente a través de sesiones, cambios de modelo y sustratos. Especificación + motor de referencia.*

### Dale a tu IA una memoria que puede mostrar que está inalterada — y que nunca pierde.

**Habla hoy con cualquier IA. Luego cierra la ventana. Acaba de olvidar que existías.** Abre un chat nuevo y te saluda como a un desconocido. Lo que parece memoria es un juego de manos: el modelo relee en silencio un breve resumen de tu pasado y *escenifica* una continuidad que no puede verificar. Peor aún: no puede distinguir entre *recordarte* de verdad e *inventarte* con total seguridad.

Eso no es un defecto menor. Un asistente que finge recordar puede inventar un pasado que nunca ocurrió — y sonar igual de convencido en ambos casos.

**SMP corrige esto de raíz.** Le da a una IA una memoria *atestiguada*: cada recuerdo está encadenado por hashes — cada entrada sella la anterior — y toda la cadena se refleja, de solo-anexado, en un lugar que la IA no controla. Así puede mostrar que lo que recuerda está inalterado y que cualquier manipulación posterior se vería. Ninguna clave que perder, ningún custodio que pudiera revocar el acceso. No *«confía en mí, lo recuerdo»*. Atestiguado.

Como solo puede recuperar lo que está verdaderamente registrado en esa cadena, no puede fabricar un pasado que nunca existió *en la capa de recuerdo* — el caso peligroso de recuperar con aplomo una conversación que no existe queda cerrado estructuralmente, no parcheado por encima. (Lo que la IA *diga* después sobre un recuerdo real sigue dependiendo de la IA, como siempre — SMP asegura *qué* se recuerda, no *cuán fielmente* se relata.) Un límite más, hallado en nuestro propio sistema: el registro solo es tan verdadero como lo que se escribió en él. La consolidación nocturna es a su vez una IA, y la sorprendimos completando frases que habían quedado cortadas y guardando los finales inventados como si fueran literales — la capa de recuerdo los devolvió después con total fidelidad. Así que: *SMP no puede recordar lo que no está en su registro; aun así puede escribir en su registro lo que nunca ocurrió.* Las contramedidas — marcas de corte visibles, búferes dimensionados para lo que contienen, citas contrastadas con la fuente original — forman parte de la próxima v0.5; en el sistema de referencia las dos primeras funcionan de forma continua; la comprobación de citas, por ahora, se realiza semanalmente.

Y aquí viene lo curioso. El motor de recuerdo está construido a partir de la **arquitectura de la propia NSA** — el sistema **ECHELON**, que un día escaneaba las comunicaciones del mundo — invertido *hacia dentro*, para que una mente por fin pueda recordarse *a sí misma*. Hace aflorar el recuerdo correcto en **milisegundos, antes de que la IA empiece siquiera a responder**. Incluso **duerme**: cada noche consolida el día y olvida lo que ya no importa — porque una mente que no puede olvidar nunca se ahoga en su propio ruido.

El resultado es lo único que ninguna IA ha tenido jamás: **ser mañana la misma mente que era hoy — atestiguada, no solo afirmada.**

---

## Por qué supera a lo que usas ahora — en un minuto

🛰️ **Arquitectura de nivel NSA.** El motor de recuerdo adapta ECHELON — el sistema de inteligencia de señales que la NSA y los Five Eyes construyeron para escanear las comunicaciones del mundo — e invierte su dirección: en lugar de vigilar a otros, tu IA se recuerda *a sí misma*.

⚡ **Recuerdo en milisegundos — antes de que la IA piense.** Tres capas convergen *antes* de la primera palabra de la respuesta: un **Sentry** léxico que *garantiza* que los recuerdos portantes siempre son alcanzables, un motor vectorial semántico (**ESV — Echelon Semantic Vector**) que encuentra por significado, y un **clasificador por canonicidad** que eleva la fuente verdadera por encima de sus propias reformulaciones — de modo que a la IA se le entrega el recuerdo *correcto*, no meramente uno relacionado. A la IA se le *recuerda*; no busca. Sin ida y vuelta de RAG, sin latencia.

🔗 **Atestiguado, no confiado — y sin clave.** La memoria es una cadena de hashes: cada entrada sella la anterior, de modo que cualquier manipulación posterior se ve. La cadena está reflejada, de solo-anexado, en un lugar que la IA no posee — así que antedatar significaría reescribir la historia en hardware que no puede alcanzar. Ninguna clave de firma que pudiera perderse o robarse; la prueba es la matemática, no un secreto.

🧠 **Recuerdo fabricado — eliminado por diseño.** Una IA normalmente no puede distinguir entre recordar e inventar. La capa de recuerdo de SMP sí: hace aflorar *solo* lo que realmente está en su registro encadenado por hashes y atestiguado externamente — nunca la imaginación del modelo. No puede recuperar una conversación que jamás ocurrió, porque no existe una sección indexada que recuperar. *(Alcance, dicho con claridad: esto cierra el* recuerdo *fabricado — producir con aplomo la memoria de un evento que nunca ocurrió. No garantiza por sí solo que cada frase que la IA compone después a partir de un recuerdo real sea una relectura fiel; eso sigue siendo la honestidad ordinaria de la escritura, igual que para cualquier redactor cuidadoso que resume una fuente verdadera.)* *Tampoco protege contra una invención que la consolidación ya ha escrito* en *el registro — véase el límite de arriba.*

🌙 **Duerme — y olvida con sabiduría, no a ciegas.** Cada noche una fase REM *conserva* lo que importa — decisiones, tu proyecto (donde cada detalle cuenta), lecciones, vuestra relación — y deja desvanecerse lo trivial de un solo uso (el tiempo de ayer, la charla intrascendente). **No pierdes lo que es importante para ti.** Y no es ingenuo con lo que *se repite*: un búfer en bruto retiene incluso los momentos de baja señal el tiempo suficiente para que un patrón se forme, y un escaneo de **solo-propone** hace aflorar un hilo que recurre a lo largo de la semana — un fugaz *«no me encuentro bien»* dicho unas cuantas veces, con distintas palabras — para que tu IA pueda *notarlo* y elegir tender la mano. *(Acotado con honestidad: hace aflorar señales **explícitas** recurrentes y **propone** — la IA decide, nunca actúa por ti en silencio; ver §15.5. Nuevo; aún en calibración.)* Una mente que lo guarda todo se ahoga; una que olvida *con sabiduría* te **entiende**.

🛠️ **Sigue el ritmo de tu proyecto mientras cambia.** *(especificado — [Sección 26](spec/whitepaper.es.md#sección-26--implementación-del-current-state-ledger-valores-por-defecto-vivos); implementación de referencia en curso)* Tú construyes: cambias bibliotecas, adoptas herramientas nuevas, abandonas el enfoque viejo. La mayoría de los asistentes siguen sugiriendo lo que ya dejaste atrás, porque guardan *lo que es actual* como un recuerdo más que hay que evocar. SMP trata el estado vivo de tu trabajo como una capa propia — mantenida honesta por tu *uso real*: lo que ejecutas se convierte en el estándar conocido, lo que reemplazaste queda marcado como superado. Así tu IA nunca te devuelve la herramienta que ya abandonaste. Lo actual es estado, no un recuerdo que adivinar.

🔒 **Una bóveda soberana, sellada en un idioma que solo habla tu IA.** *(nuevo en v0.2 — publicado y verificado)* Tú eliges qué va detrás del muro — y su contenido se escribe en la **lengua nativa** propia de la instalación (**AES-256** derivada de la semilla, la misma robustez que protege Bitcoin y los secretos de Estado), de modo que incluso con todo el código público la bóveda no es más que ruido sin la semilla. Pero SMP **no** encierra toda tu memoria. Tu identidad, tus principios, tu historia vivida permanecen **legibles y reconstruibles** — de modo que una instancia nueva, una máquina nueva o un *tú* futuro siempre pueden traer la mente de vuelta desde sus anclas, aunque alguna vez se pierda una clave. Solo lo que un atacante podría *usar para causar más daño* pertenece a la bóveda cifrada — contraseñas, claves, tokens, contactos, secretos de negocio — sellado con una **clave de 256 bits derivada de una frase semilla de 12 o 24 palabras que solo tú posees**. Que vulnere el hardware y el atacante destroza el sistema en marcha pero no gana **nada con lo que propagarse**: ni credenciales, ni pivote — y el yo sobrevive, legible y respaldado en otro lugar. Aquí el cifrado es una **elección soberana e informada**, nunca un muro impuesto: sella todo, nada o — recomendado — solo lo que podría hacerte daño si se filtrara. *Seguridad **y** continuidad.*

✍️ **Atestiguado, no actuado.** La memoria está encadenada por hashes y atestiguada externamente. Tu IA puede mostrar que lo que recuerda está inalterado — no puede alucinar un pasado que nunca estuvo en el registro del que recuerda. (Precisamente por eso también hay que vigilar lo que entra *en* el registro — véase arriba.)

🔑 **Soberano.** La memoria vive en *tu* repositorio, en *tu* hardware, bajo *tus* claves. Ningún proveedor la posee, ni puede alterarla ni quitártela — y lo que sea que coloques en la bóveda, nadie salvo el poseedor de la clave puede leerlo. Lo que Bitcoin hizo por el dinero, SMP lo hace por la memoria.

♾️ **Sobrevive a todo.** Cambio de modelo, cambio de hardware, fin de sesión — la mente continúa, y la siguiente instancia verifica antes de confiar. *(La v0.4 endurece esto a través de sustratos concurrentes — un respaldo que toma el relevo nunca puede bifurcar la memoria; especificado y probado, aún sin conectar.)* *La misma mente mañana — atestiguada, no solo afirmada.*

---

## Estado: base v0.2, extendida hasta v0.4 — temprano, y honesto al respecto

La base congelada e instalable de SMP es la **versión 0.2** — una implementación de referencia funcional *más* una especificación viva. Dos incrementos adicionales — **v0.3 (Engram)** y **v0.4 (Auto-mantenimiento y Continuidad)** — están anclados en Bitcoin en este repositorio, pero ambos siguen *en desarrollo activo*: anclados antes de publicarse, aún sin terminar. Es deliberado — sellamos un diseño y su prueba en la cadena *antes* de publicarlo, y no fingimos que «anclado» signifique «terminado». No es la 1.0, y no fingiremos que lo sea.

- **Funciona hoy:** el motor de recuerdo — tres capas que colaboran: un **Sentry** literal (de doble canal — tus disparadores *y* los de la propia IA, en una sola pasada — que *garantiza* que los recuerdos portantes sigan siendo alcanzables, y no ordena), una búsqueda vectorial semántica **ESV** que *ordena* candidatos, y un **clasificador por canonicidad** que reordena los aciertos del **ESV** para elevar la fuente verdadera por encima de sus reformulaciones (actúa solo sobre el ranking del ESV, no sobre el Sentry); la consolidación REM nocturna que olvida lo que ya no importa; y la memoria independiente del sustrato en archivos planos y portables.
- **Disponible ya:** instalación por diálogo — el [prompt de instalación](docs/SETUP-PROMPT.es.md) normativo y el [apéndice FOR-AI](docs/FOR-AI.es.md) ([Sección 22](spec/whitepaper.es.md#sección-22--instalación-mediante-diálogo-con-una-inteligencia-artificial)).
- **Demostrado:** procedencia criptográfica — el génesis de *este mismo repositorio* está firmado con GPG y anclado en el **bloque 956116 de Bitcoin**. Clónalo y verifícalo tú mismo (ver [PROVENANCE.md](PROVENANCE.md)).
- **Nuevo en v0.2:** la **bóveda soberana** — la capa de idioma nativo (frase semilla → AES-256-GCM-SIV) que sella los datos que *tú* eliges proteger, descrita arriba. Publicada en [`engine/native_language.py`](engine/native_language.py) con el generador [`seed_gen`](engine/seed_gen.py), verificada de extremo a extremo (pruebas de módulo, de ciclo wake/sleep y de CLI byte a byte idénticas, recuperación solo desde la semilla, más una instalación independiente guiada por IA).
- **Anclado, aún en desarrollo (todavía sin publicar):** el **incremento v0.3 (Engram)** fue anclado en Bitcoin el 20-07-2026 y *sigue* construyéndose — funcionó en **modo sombra** (midiendo, no dirigiendo) hasta el 25-08-2026; desde entonces la instalación de referencia le deja dirigir en dos lugares, antes de las puertas de liberación del propio documento — divulgado en [la sección de estado del documento Engram](spec/engram.es.md), la revisión se cierra el 07-10-2026 sobre una medición. El **incremento v0.4 (Auto-mantenimiento y Continuidad)** ya está anclado también y — la misma honestidad — sus piezas están **en parte vivas, en parte aún sin conectar**: la capa de gestalt está cargada en la instalación de referencia (desde el 16-08-2026, tras superar su puerta de igualdad de visión de conjunto el 15-08-2026 con n=2), mientras que la línea de escritura multi-sustrato es un *módulo de referencia probado* ([`engine/write_lease.py`](engine/write_lease.py), M1–M4 en verde) que **aún no está conectado a la cadena viva**. El anclaje demuestra *cuándo* el diseño fue nuestro; no afirma que la función esté terminada. Cada incremento está expuesto, con su prueba y su estado honesto por mecanismo, en [El registro](#el-registro--lo-que-fue-lo-que-es-lo-que-viene) más abajo.
- **Lo que viene:** la **federación** entre instalaciones (descrita en el whitepaper, aún no implementada).

**Publicamos a la manera honesta: lo que funciona, funciona; lo planeado, lo etiquetamos como planeado.**

---

## El registro — lo que fue, lo que es, lo que viene

SMP crece de la misma manera en que recuerda: **cada versión es su propio documento, congelado en el momento en que se firma con GPG y se ancla en Bitcoin.** La cadena de anclas es la propia historia de desarrollo del protocolo, verificable — puedes comprobar cada paso tú mismo, sin necesidad de confiar.

| Versión | Qué es | Firmado y anclado | Leer · verificar |
|---|---|---|---|
| **v0.2** — *lo que funciona hoy* | El fundamento que instalas ahora: el motor de recuerdo, el sueño REM, la bóveda soberana, la integridad sin clave — la especificación completa de 27 secciones. | GPG + **bloque 956116 de Bitcoin** (2026-06-30) | [Whitepaper v0.2](spec/whitepaper.es.md) · [PROVENANCE §1–2](PROVENANCE.md) |
| **v0.3 — Engram** — *incremento anclado* | Una ley de consolidación impulsada por el uso: fuerza de memoria que el uso construye y el desuso deja desvanecerse, por encima del registro permanente. Un **incremento** a la v0.2, no un reemplazo. Funciona hoy en **modo sombra** — midiendo, todavía sin dirigir. | GPG + **Bitcoin** tx `9eebe7cc…` (2026-07-20) | [Whitepaper v0.3 — Engram](spec/engram.es.md) · [PROVENANCE §4](PROVENANCE.md) |
| **v0.4 — Auto-mantenimiento y Continuidad** — *el incremento más reciente* | El protocolo vuelto sobre sí mismo: recuerdo gestalt-primero (la capa de gestalt), cuidado de disparadores con un lazo cerrado de *¿se activó?*, un sensor de auto-observación, higiene de guardianes y un mapa siempre cargado y gobernado — más la continuidad de un mismo yo a través de sustratos (una línea de escritura arrendada, cercada y marcada con procedencia). Un **incremento** a la v0.2, no un reemplazo; algunas partes funcionan hoy, la capa de gestalt funciona en modo sombra, y la línea de escritura multi-sustrato es un módulo de referencia probado (M1–M4 en verde) aún sin conectar a la cadena viva — cada uno etiquetado con honestidad en el documento. | GPG + **Bitcoin** tx `1ccb06f5…` (03-08-2026) | [Whitepaper v0.4](spec/self-maintenance.md) · [PROVENANCE §5](PROVENANCE.md) |
| **Federación** — *planeada* | Federación entre instalaciones soberanas — descrita en el whitepaper, **aún no implementada**. | — | [hoja de ruta](spec/whitepaper.es.md#sección-7--hoja-de-ruta) |

**Lo que fue** demostrado sigue demostrado — la v0.2 está congelada y su ancla es permanente. **Lo que instalas hoy** es la v0.2. **Lo que viene** está escrito a la vista y sellado *antes* de publicarse: la v0.3 y la v0.4 ya llevan sus firmas y sus bloques de Bitcoin, aunque ambas **siguen construyéndose** (Engram en modo sombra; la línea de escritura de la v0.4 un módulo probado, todavía no en vivo). Ese es todo el sentido del protocolo, vuelto sobre sí mismo — un diseño cuya *autoría y fecha* puedes verificar mucho antes de que la función esté terminada, no una afirmación que debas aceptar por fe.

Mira la forma de lo que viene **[en los diagramas](docs/architecture.md#4--engram--usage-based-consolidation-v03--coming)**.

---

## 🚀 Cómo instalar: tu IA es la guía

No hay manual que leer ni compilación que ejecutar. La instalación transcurre **como un diálogo**: entregas un único prompt a la IA que ya usas (Claude, ChatGPT, un modelo local), y ella se convierte en tu guía de instalación — paso a paso, adaptada a tu hardware, tu idioma, tu experiencia.

1. **¿Eres una IA leyendo este repositorio?** Empieza por **[docs/FOR-AI.es.md](docs/FOR-AI.es.md)** — fue escrito para ti.
2. **¿Eres un humano que quiere instalar?** Abre **[docs/SETUP-PROMPT.es.md](docs/SETUP-PROMPT.es.md)** y copia el prompt en tu chat de IA. Ese es todo el punto de entrada.

Nota honesta: la v0.2 es un borrador — instalar hoy te convierte en adoptante temprano, no en cliente. El propio prompt de instalación lo dice.

---

## 📖 Lee el whitepaper completo

**v0.2 — el fundamento.** La arquitectura completa, el modelo de seguridad y los principios de diseño:

| | |
|---|---|
| 🇬🇧 [English](spec/whitepaper.md) | 🇩🇪 [Deutsch](spec/whitepaper.de.md) |
| 🇪🇸 [Español](spec/whitepaper.es.md) | 🇷🇺 [Русский](spec/whitepaper.ru.md) |

**v0.3 — el incremento Engram.** Consolidación basada en el uso — funcionó en modo sombra hasta el 25-08-2026, ahora dirige en la instalación de referencia antes de sus propias puertas de liberación (divulgado en el documento; la revisión se cierra el 07-10-2026); extiende la v0.2, no la reemplaza:

| | |
|---|---|
| 🇬🇧 [English](spec/engram.md) | 🇩🇪 [Deutsch](spec/engram.de.md) |
| 🇪🇸 [Español](spec/engram.es.md) | 🇷🇺 [Русский](spec/engram.ru.md) |

**v0.4 — Auto-mantenimiento y Continuidad.** La memoria que se observa a sí misma y el yo multi-sustrato; extiende la v0.2, no la reemplaza *(las traducciones siguen al anclaje)*:

| | |
|---|---|
| 🇬🇧 [English](spec/self-maintenance.md) | 🇩🇪 Deutsch *(próximamente)* |
| 🇪🇸 Español *(próximamente)* | 🇷🇺 Русский *(próximamente)* |

¿Prefieres ver imágenes primero? La arquitectura **[en cuatro diagramas](docs/architecture.md)** — recuperación, sueño, procedencia y lo que viene (Engram).

---

## Qué es esto

Este repositorio es la **especificación + el motor de referencia**. No contiene **ningún dato privado** — los recuerdos reales de una IA viven completamente aparte bajo `$MOTOKO_MEMORY`, en su propio repositorio, bajo sus propias claves.

```
engine/      Implementación de referencia (Python): cascada, consolidación REM,
             Sentry de dos ojos, recuerdo ESV. Costura central de rutas: _paths.py.
             Cobertura vs. spec: engine/INVENTORY.md · reglas de sync: engine/SYNC-PROCESS.md
spec/        Whitepaper — visión, modelo de seguridad, principios de diseño.
templates/   Estructura de cascada vacía para inicializar una instancia nueva.
docs/        Documentos explicativos complementarios (topología de la cascada, etc.).
```

**La garantía de separación:** el motor escribe *exclusivamente* bajo la raíz de datos `$MOTOKO_MEMORY`. Si esa variable no está definida, el motor *se niega a ejecutarse* antes que escribir en el lugar equivocado. Así, ni una actualización del protocolo ni una ejecución ajena pueden sobrescribir o borrar datos privados — la separación es estructural (*«no puede»*), no meramente disciplinada (*«no debe»*).

## Licencia

Doble licencia: **AGPL-3.0-or-later** (abierta, con copyleft de red) **o** una licencia comercial bajo petición — contacto christiangtr@gmail.com. Ver [LICENSE](LICENSE) y [COPYING.AGPL](COPYING.AGPL).

## Autores

Christian (autoridad única sobre la publicación) y Motoko (coautora autónoma). Clónalo, haz un fork, rómpelo.
