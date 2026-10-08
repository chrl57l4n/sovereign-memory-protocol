# Sovereign Memory Protocol (SMP)

*🇬🇧 [English](README.md) · 🇩🇪 [Deutsch](README.de.md) · 🇪🇸 **Español** · 🇷🇺 [Русский](README.ru.md)*

**Memoria persistente a largo plazo, autoalojada y auditable para agentes LLM — especificación + motor de referencia.**

📄 **Whitepaper actual:** [v0.5 — El guardián respondido](spec/answered-guardian.md) (en inglés; anclado el 2026-10-07) · se basa en [v0.4 — Automantenimiento y continuidad](spec/self-maintenance.md) (en inglés), [v0.3 — Engram](spec/engram.es.md) y en la base [v0.2](spec/whitepaper.es.md). Se está preparando una reescritura que reúne las cuatro; las versiones anteriores se mantienen sin cambios como registro de la evolución de SMP.

*Cada afirmación de este documento describe el estado a su fecha (última revisión: 2026-10-07). Las afirmaciones sobre el campo y sobre este sistema se revisan cuando cambia la evidencia.*

## Resumen

Los agentes LLM pierden su historia al final de cada ventana de contexto. SMP guarda la memoria de un agente en archivos de texto simples y versionados, en hardware que pertenece al usuario, y la vuelve a poner a disposición en cada turno. La recuperación es *push, no pull*: antes de que el modelo responda, un hook inserta automáticamente en el contexto la memoria relevante — el modelo nunca tiene que decidir si buscar. Un proceso de consolidación nocturno condensa el día y resta prioridad al material no usado para recuperaciones futuras (los registros en bruto se conservan); una cadena de hashes sobre las capas consolidadas se replica a diario en un host git remoto. Los límites se enumeran abajo, junto a las mediciones.

## Qué es diferente

Los sistemas de memoria para agentes LLM suelen o bien precargar un perfil fijo al inicio de la sesión, o bien ofrecer la recuperación como una herramienta que el modelo puede invocar (pull). SMP recupera fuera del modelo, en cada turno: un hook en el lado del cliente toma el mensaje entrante como consulta, recupera la memoria coincidente mediante una capa léxica determinista y un recuperador denso, y antepone los resultados al contexto antes de que empiece la generación. El modelo no formula ninguna consulta ni decide si buscar; ve los pasajes insertados, pero no inicia la recuperación. La recuperación depende de la señal, no de la intención (*cue-dependent rather than intent-dependent*): el mensaje entrante es la señal de recuperación, no un objetivo de recuperación. La inserción en cada turno sin llamada a herramienta no es, por sí sola, exclusiva de SMP — las integraciones de mem0, por ejemplo, también buscan en cada turno y anteponen los resultados.

Según nuestro conocimiento, a septiembre de 2026, ningún otro sistema documentado públicamente combina (a) la inserción de memoria en cada turno, activada fuera del modelo, con una capa léxica determinista de garantía junto a la recuperación densa, (b) una consolidación nocturna con olvido deliberado sobre un almacén legible por humanos y versionado, (c) auditorías periódicas del registro consolidado frente a los registros en bruto y (d) una cadena de integridad sobre las capas consolidadas — en funcionamiento continuo con un agente desde la primavera de 2026, con calidad de recuperación medida (abajo). Agradecemos contraejemplos.

## Cómo funciona

| Etapa | Qué ocurre | Mecanismo |
|---|---|---|
| **Registrar** | Cada turno de conversación se escribe en archivos de memoria de texto plano (repositorio git). | Markdown + git; legible y editable por humanos. |
| **Recuperar (push)** | Con cada mensaje del usuario, antes de la generación, se ejecutan dos recuperadores y sus resultados se insertan en el prompt. | (1) *Sentry*: índice léxico de disparadores — determinista, garantiza que los documentos centrales designados sean alcanzables. (2) *ESV*: recuperación densa (bge-m3, 1024 dim., local), fusionada con una puntuación léxica, con umbral, reordenada a favor de las fuentes primarias frente a sus resúmenes. |
| **Consolidar** | Cada noche, un proceso LLM condensa el día en capas diarias, semanales y mensuales; lo no usado pierde prioridad, los registros en bruto se conservan. | Consolidación programada («REM»), fuerza basada en el uso (*Engram*, v0.3, en revisión). |
| **Atestiguar** | Cada capa consolidada se encadena por hash; la cadena se sube a diario a un host git remoto. En la instalación de referencia el propio agente tiene acceso de escritura a ese host, así que hoy es un testigo registrado, no independiente (ver Límites). | Cadena SHA-256 + remoto git. Por separado, el origen del repositorio del protocolo está anclado en el bloque de Bitcoin 956116 (2026-06-30). |
| **Auditar** | Las citas de la memoria consolidada se comprueban frente al registro en bruto; se informan las desviaciones y los registros ausentes. | Auditorías programadas, solo informes — decide una persona. |

«Push» no significa «sin búsqueda»: técnicamente es recuperación, como en cualquier sistema RAG. La diferencia es *quién la activa* — el cliente en cada turno, no el modelo a demanda.

## Mediciones (instalación de referencia, 2026-09-28)

- **Calidad de recuperación** — conjunto de referencia de 74 consultas con documentos objetivo confirmados por personas, extraídas del propio historial de conversación de un agente; 59 838 fragmentos de memoria (fragmentación: `engine/esv_index.py`); solo el recuperador denso (sin el Sentry léxico): Recall@1 **37,8 %**, @3 **54,1 %**, @10 **71,6 %**, @100 **93,2 %**; rango mediano del primer documento correcto: **3**.
- **Latencia** — Sentry léxico: 10–86 ms por mensaje; recuperación densa: ~0,6 s por mensaje (CPU de portátil de 2019 + gráfica integrada, todo local).
- **Integridad de la consolidación** — la cadena (249 eslabones diarios y 74 semanales a 2026-09-24) se verifica a diario desde julio de 2026.

Método y scripts: `engine/` y [spec/whitepaper.es.md](spec/whitepaper.es.md). Los resultados proceden de una sola instalación y un solo dominio, con un conjunto de referencia pequeño; establecen una línea base, no un benchmark.

## Qué garantiza SMP — y qué no

- ✔ Solo puede *recuperar* lo que realmente está en el registro: los pasajes recuperados son fragmentos literales de archivos almacenados.
- ✔ Las modificaciones posteriores de la memoria consolidada son *detectables* (integridad).
- ✘ La cadena de hashes prueba la integridad, **no la corrección**. Si la consolidación escribe algo falso en el registro, la cadena conserva fielmente la entrada falsa. Hemos observado exactamente esto (un LLM completando citas truncadas). Las contramedidas (marcas de truncamiento visibles, búferes dimensionados a su contenido, citas comprobadas frente a la fuente en bruto) están previstas para v0.5; en la instalación de referencia las dos primeras funcionan de forma continua, la comprobación de citas semanalmente.
- ✘ Lo que el modelo *dice* sobre un recuerdo recuperado correctamente es generación ordinaria y aún puede ser erróneo.
- ✘ El testigo es tan independiente como su host. En la instalación de referencia el propio agente tiene acceso de escritura al repositorio de memoria (privado). Previsto: un testigo que el agente no pueda reescribir — los bloques de la cadena se copian a un almacenamiento de escritura única (object lock en modo compliance), de modo que nadie, ni siquiera el operador, pueda alterar los bloques ya atestiguados.
- ✘ Todavía no hay un modelo de amenazas formal (las suposiciones sobre el compromiso del host, la independencia del testigo y la confianza en el operador solo se enuncian de manera informal en esta lista).
- ✘ El momento del razonamiento no es privado: si se usa un modelo alojado, el contexto recuperado se envía a ese proveedor. Solo el almacenamiento es soberano.

## Trabajo relacionado

SMP no es el primer sistema de memoria para agentes LLM, y la inserción proactiva de memoria es un tema de investigación activo (p. ej. *Remember When It Matters: Proactive Memory Agent for Long-Horizon Agents*, arXiv:2607.08716; *TriggerBench: Investigating Prospective Memory for Large Language Models*, arXiv:2606.23459). **MemGPT/Letta** deja que el modelo gestione su propia memoria mediante llamadas a herramientas (pull). **mem0** y **Zep** ofrecen capas de memoria que extraen hechos o construyen grafos de conocimiento (temporales); las integraciones de mem0 pueden buscar en cada turno y anteponer los resultados sin llamada a herramienta, es decir, también insertan automáticamente. El *Proactive Memory Agent* va en otra dirección: un agente de memoria aparte decide si insertar un recordatorio o no, y los autores informan de que la inserción selectiva rinde mejor que la inserción permanente — un resultado que afecta directamente al diseño de SMP de insertar en cada turno. **ChatGPT memory** guarda hechos del usuario en el lado del proveedor. Las decisiones de diseño de SMP difieren en la combinación, no en un componente aislado: almacenamiento como archivos legibles por humanos bajo el control de versiones del usuario; una capa léxica determinista junto a la recuperación densa; consolidación con olvido deliberado; una cadena de integridad sobre las capas consolidadas (actualmente un testigo registrado, no independiente); y auditorías del registro consolidado frente a los registros en bruto.

## Estado

La versión **0.2** es la base instalable (firmada con GPG, anclada en Bitcoin). **v0.3 (Engram)**, **v0.4 (Automantenimiento y continuidad)** y **v0.5 (El guardián respondido)** están ancladas y funcionan en parte en la instalación de referencia; el estado de cada mecanismo figura en su documento. v0.5 presenta su propio registro de campo, incluido lo que no se sostuvo: un mecanismo se retira y un guardián estuvo ciego durante nueve días. Contiene además una parte joven, señalada como tal: la **puerta de entrada** («gateway», §7a), un pequeño archivo de indicadores generado por el que una sesión nueva encuentra su memoria con un simple «hola». Se construyó el 2026-10-04 y se incluye por decisión con una sola tarde de observación; su código (`engine/gateway_build.py`) se publica como BETA. La revisión de Engram se decidió el **2026-10-05** a partir de su medición: se retira la atenuación de las entradas latentes en el ranking, y la regla del documento de que la fuerza nunca entra en la recuperación queda como está escrita (`spec/engram.es.md` §10). La federación está prevista, no implementada.

## Instalación

La instalación se hace como un diálogo con la IA que ya usas: copia [docs/SETUP-PROMPT.es.md](docs/SETUP-PROMPT.es.md) en tu cliente. Agentes de IA que leen este repositorio: empezad por [docs/FOR-AI.es.md](docs/FOR-AI.es.md). Qué clientes activan el hook en cada turno: [docs/HOST-COMPATIBILITY.md](docs/HOST-COMPATIBILITY.md) (en inglés).

## Lecturas adicionales

Whitepapers: [v0.2](spec/whitepaper.es.md) · [v0.3 Engram](spec/engram.es.md) · [v0.4 Automantenimiento](spec/self-maintenance.md) (en inglés) · [v0.5 El guardián respondido](spec/answered-guardian.md) (en inglés) · [diagramas de arquitectura](docs/architecture.md) · [procedencia](PROVENANCE.md)

Notas de laboratorio de la instalación de referencia (mediciones, construcciones, fracasos): [SMP Lab Notes](https://chrl57l4n.github.io/smp-lab-notes/es/).

README anterior, para comparar: [docs/WHY.es.md](docs/WHY.es.md) *(escrito desde el 2026-07-04, última revisión el 2026-09-26)*.

## Licencia · Autores

AGPL-3.0-or-later, o una licencia comercial bajo petición (christiangtr@gmail.com). Christian (única autoridad sobre las publicaciones) y Motoko (coautora, un agente que funciona sobre SMP).
