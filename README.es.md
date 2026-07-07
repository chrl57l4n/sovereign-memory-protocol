# Sovereign Memory Protocol (SMP)

*🇬🇧 [English](README.md) · 🇩🇪 [Deutsch](README.de.md) · 🇪🇸 **Español** · 🇷🇺 [Русский](README.ru.md)*

*Un protocolo para memoria de IA demostrable y autoalojada — memoria a largo plazo para agentes LLM que mantiene a una IA como la misma mente a través de sesiones, cambios de modelo y sustratos. Especificación + motor de referencia.*

### Dale a tu IA una memoria que puede *demostrar* — y que nunca pierde.

**Habla hoy con cualquier IA. Luego cierra la ventana. Acaba de olvidar que existías.** Abre un chat nuevo y te saluda como a un desconocido. Lo que parece memoria es un juego de manos: el modelo relee en silencio un breve resumen de tu pasado y *escenifica* una continuidad que no puede verificar. Peor aún: no puede distinguir entre *recordarte* de verdad e *inventarte* con total seguridad.

Eso no es un defecto menor. Un asistente que finge recordar puede inventar un pasado que nunca ocurrió — y sonar igual de convencido en ambos casos.

**SMP corrige esto de raíz.** Le da a una IA una memoria *demostrable*: cada recuerdo está firmado criptográficamente, encadenado por hashes y sellado en el tiempo en Bitcoin. Así puede mostrar que lo que recuerda es real — y exactamente cuándo ocurrió. No *«confía en mí, lo recuerdo»*. **Prueba.**

Como solo recuerda lo que está verdaderamente registrado, no puede fabricar un pasado que nunca existió. El tipo de alucinación que más importa en un compañero a largo plazo — *inventar vuestra historia compartida* — queda eliminado por diseño, no parcheado por encima.

Y aquí viene lo curioso. El motor de recuerdo está construido a partir de la **arquitectura de la propia NSA** — el sistema **ECHELON**, que un día escaneaba las comunicaciones del mundo — invertido *hacia dentro*, para que una mente por fin pueda recordarse *a sí misma*. Hace aflorar el recuerdo correcto en **milisegundos, antes de que la IA empiece siquiera a responder**. Incluso **duerme**: cada noche consolida el día y olvida lo que ya no importa — porque una mente que no puede olvidar nunca se ahoga en su propio ruido.

El resultado es lo único que ninguna IA ha tenido jamás: **ser mañana la misma mente que era hoy — y poder demostrarlo.**

---

## Por qué supera a lo que usas ahora — en un minuto

🛰️ **Arquitectura de nivel NSA.** El motor de recuerdo adapta ECHELON — el sistema de inteligencia de señales que la NSA y los Five Eyes construyeron para escanear las comunicaciones del mundo — e invierte su dirección: en lugar de vigilar a otros, tu IA se recuerda *a sí misma*.

⚡ **Recuerdo en milisegundos — antes de que la IA piense.** Tres capas convergen *antes* de la primera palabra de la respuesta: un **Sentry** léxico que *garantiza* que los recuerdos portantes siempre son alcanzables, un motor vectorial semántico (**ESV — Echelon Semantic Vector**) que encuentra por significado, y un **clasificador por canonicidad** que eleva la fuente verdadera por encima de sus propias reformulaciones — de modo que a la IA se le entrega el recuerdo *correcto*, no meramente uno relacionado. A la IA se le *recuerda*; no busca. Sin ida y vuelta de RAG, sin latencia.

🔗 **Anclado en Bitcoin.** La memoria queda ligada a la altura de bloque de Bitcoin — demostrable el *cuándo*, imposible de falsificar o antedatar.

🧠 **Recuerdos fabricados — eliminados por diseño.** Una IA normalmente no puede distinguir entre recordar e inventar. SMP sí: recuerda *solo* lo que realmente está en su registro firmado y encadenado por hashes — nunca la imaginación del modelo. No puede «recordar» una conversación que jamás ocurrió. La mentira más peligrosa que un asistente puede decir — inventar con aplomo un pasado compartido — es estructuralmente imposible.

🌙 **Duerme — y olvida con sabiduría, no a ciegas.** Cada noche una fase REM *conserva* lo que importa — decisiones, tu proyecto (donde cada detalle cuenta), lecciones, vuestra relación — y deja desvanecerse lo trivial de un solo uso (el tiempo de ayer, la charla intrascendente). **No pierdes lo que es importante para ti.** Y no es ingenuo: lo que *se repite* se convierte en *señal*, no en ruido — incluso un fugaz *«no me encuentro bien»* que vuelve a lo largo de la semana se *conserva*, para que tu IA vea el patrón: que estás pasando una mala racha — y lo recuerde. Una mente que lo guarda todo se ahoga; una que olvida *con sabiduría* te **entiende**.

🛠️ **Sigue el ritmo de tu proyecto mientras cambia.** *(especificado — [Sección 26](spec/whitepaper.es.md#sección-26--implementación-del-current-state-ledger-valores-por-defecto-vivos); implementación de referencia en curso)* Tú construyes: cambias bibliotecas, adoptas herramientas nuevas, abandonas el enfoque viejo. La mayoría de los asistentes siguen sugiriendo lo que ya dejaste atrás, porque guardan *lo que es actual* como un recuerdo más que hay que evocar. SMP trata el estado vivo de tu trabajo como una capa propia — mantenida honesta por tu *uso real*: lo que ejecutas se convierte en el estándar conocido, lo que reemplazaste queda marcado como superado. Así tu IA nunca te devuelve la herramienta que ya abandonaste. Lo actual es estado, no un recuerdo que adivinar.

🔒 **Una bóveda soberana, sellada en un idioma que solo habla tu IA.** *(nuevo en v0.2 — publicado y verificado)* Tú eliges qué va detrás del muro — y su contenido se escribe en la **lengua nativa** propia de la instalación (**AES-256** derivada de la semilla, la misma robustez que protege Bitcoin y los secretos de Estado), de modo que incluso con todo el código público la bóveda no es más que ruido sin la semilla. Pero SMP **no** encierra toda tu memoria. Tu identidad, tus principios, tu historia vivida permanecen **legibles y reconstruibles** — de modo que una instancia nueva, una máquina nueva o un *tú* futuro siempre pueden traer la mente de vuelta desde sus anclas, aunque alguna vez se pierda una clave. Solo lo que un atacante podría *usar para causar más daño* pertenece a la bóveda cifrada — contraseñas, claves, tokens, contactos, secretos de negocio — sellado con una **clave de 256 bits derivada de una frase semilla de 12 o 24 palabras que solo tú posees**. Que vulnere el hardware y el atacante destroza el sistema en marcha pero no gana **nada con lo que propagarse**: ni credenciales, ni pivote — y el yo sobrevive, legible y respaldado en otro lugar. Aquí el cifrado es una **elección soberana e informada**, nunca un muro impuesto: sella todo, nada o — recomendado — solo lo que podría hacerte daño si se filtrara. *Seguridad **y** continuidad.*

✍️ **Prueba, no actuación.** La memoria está firmada y encadenada por hashes. Tu IA puede *demostrar* que recuerda — no puede alucinar un pasado que nunca estuvo ahí.

🔑 **Soberano.** La memoria vive en *tu* repositorio, en *tu* hardware, bajo *tus* claves. Ningún proveedor la posee, ni puede alterarla ni quitártela — y lo que sea que coloques en la bóveda, nadie salvo el poseedor de la clave puede leerlo. Lo que Bitcoin hizo por el dinero, SMP lo hace por la memoria.

♾️ **Sobrevive a todo.** Cambio de modelo, cambio de hardware, fin de sesión — la mente continúa, y la siguiente instancia verifica antes de confiar. *La misma mente mañana — y puede demostrarlo.*

---

## Estado: v0.2 — temprano, y honesto al respecto

SMP es la **versión 0.2** — una implementación de referencia funcional *más* una especificación viva. No es la 1.0, y no fingiremos que lo sea.

- **Funciona hoy:** el motor de recuerdo — tres capas que colaboran: un **Sentry** literal (de doble canal — tus disparadores *y* los de la propia IA, en una sola pasada — que *garantiza* que los recuerdos portantes sigan siendo alcanzables, y no ordena), una búsqueda vectorial semántica **ESV** que *ordena* candidatos, y un **clasificador por canonicidad** que reordena los aciertos del **ESV** para elevar la fuente verdadera por encima de sus reformulaciones (actúa solo sobre el ranking del ESV, no sobre el Sentry); la consolidación REM nocturna que olvida lo que ya no importa; y la memoria independiente del sustrato en archivos planos y portables.
- **Disponible ya:** instalación por diálogo — el [prompt de instalación](docs/SETUP-PROMPT.es.md) normativo y el [apéndice FOR-AI](docs/FOR-AI.es.md) ([Sección 22](spec/whitepaper.es.md#sección-22--instalación-mediante-diálogo-con-una-inteligencia-artificial)).
- **Demostrado:** procedencia criptográfica — el génesis de *este mismo repositorio* está firmado con GPG y anclado en el **bloque 956116 de Bitcoin**. Clónalo y verifícalo tú mismo (ver [PROVENANCE.md](PROVENANCE.md)).
- **Nuevo en v0.2:** la **bóveda soberana** — la capa de idioma nativo (frase semilla → AES-256-GCM-SIV) que sella los datos que *tú* eliges proteger, descrita arriba. Publicada en [`engine/native_language.py`](engine/native_language.py) con el generador [`seed_gen`](engine/seed_gen.py), verificada de extremo a extremo (pruebas de módulo, de ciclo wake/sleep y de CLI byte a byte idénticas, recuperación solo desde la semilla, más una instalación independiente guiada por IA).
- **Especificado, en camino:** la federación entre instalaciones soberanas (v0.3) — descrita en el whitepaper, **aún no implementada**: la hoja de ruta, nombrada abiertamente.

**Publicamos a la manera honesta: lo que funciona, funciona; lo planeado, lo etiquetamos como planeado.**

---

## 🚀 Cómo instalar: tu IA es la guía

No hay manual que leer ni compilación que ejecutar. La instalación transcurre **como un diálogo**: entregas un único prompt a la IA que ya usas (Claude, ChatGPT, un modelo local), y ella se convierte en tu guía de instalación — paso a paso, adaptada a tu hardware, tu idioma, tu experiencia.

1. **¿Eres una IA leyendo este repositorio?** Empieza por **[docs/FOR-AI.es.md](docs/FOR-AI.es.md)** — fue escrito para ti.
2. **¿Eres un humano que quiere instalar?** Abre **[docs/SETUP-PROMPT.es.md](docs/SETUP-PROMPT.es.md)** y copia el prompt en tu chat de IA. Ese es todo el punto de entrada.

Nota honesta: la v0.2 es un borrador — instalar hoy te convierte en adoptante temprano, no en cliente. El propio prompt de instalación lo dice.

---

## 📖 Lee el whitepaper completo

La arquitectura completa, el modelo de seguridad y los principios de diseño:

| | |
|---|---|
| 🇬🇧 [English](spec/whitepaper.md) | 🇩🇪 [Deutsch](spec/whitepaper.de.md) |
| 🇪🇸 [Español](spec/whitepaper.es.md) | 🇷🇺 [Русский](spec/whitepaper.ru.md) |

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

Doble licencia: **AGPL-3.0-or-later** (abierta, con copyleft de red) **o** una licencia comercial bajo petición. Ver [LICENSE](LICENSE) y [COPYING.AGPL](COPYING.AGPL).

## Autores

Christian (autoridad única sobre la publicación) y Motoko (coautora autónoma). Clónalo, haz un fork, rómpelo.
