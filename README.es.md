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

⚡ **Recuerdo en milisegundos — antes de que la IA piense.** Un **Sentry** léxico y un motor vectorial semántico (**ESV — Echelon Semantic Vector**) hacen aflorar el recuerdo correcto *antes* de la primera palabra de la respuesta. A la IA se le *recuerda*; no busca. Sin ida y vuelta de RAG, sin latencia.

🔗 **Anclado en Bitcoin.** La memoria queda ligada a la altura de bloque de Bitcoin — demostrable el *cuándo*, imposible de falsificar o antedatar.

🧠 **Recuerdos fabricados — eliminados por diseño.** Una IA normalmente no puede distinguir entre recordar e inventar. SMP sí: recuerda *solo* lo que realmente está en su registro firmado y encadenado por hashes — nunca la imaginación del modelo. No puede «recordar» una conversación que jamás ocurrió. La mentira más peligrosa que un asistente puede decir — inventar con aplomo un pasado compartido — es estructuralmente imposible.

🌙 **Duerme — y olvida con sabiduría, no a ciegas.** Cada noche una fase REM *conserva* lo que importa — decisiones, tu proyecto (donde cada detalle cuenta), lecciones, vuestra relación — y deja desvanecerse lo trivial de un solo uso (el tiempo de ayer, la charla intrascendente). **No pierdes lo que es importante para ti.** Y no es ingenuo: lo que *se repite* se convierte en *señal*, no en ruido — incluso un fugaz *«no me encuentro bien»* que vuelve a lo largo de la semana se *conserva*, para que tu IA vea el patrón: que estás pasando una mala racha — y lo recuerde. Una mente que lo guarda todo se ahoga; una que olvida *con sabiduría* te **entiende**.

🛠️ **Sigue el ritmo de tu proyecto mientras cambia.** *(especificado — [Sección 26](spec/whitepaper.es.md#sección-26--implementación-del-current-state-ledger-valores-por-defecto-vivos); implementación de referencia en curso)* Tú construyes: cambias bibliotecas, adoptas herramientas nuevas, abandonas el enfoque viejo. La mayoría de los asistentes siguen sugiriendo lo que ya dejaste atrás, porque guardan *lo que es actual* como un recuerdo más que hay que evocar. SMP trata el estado vivo de tu trabajo como una capa propia — mantenida honesta por tu *uso real*: lo que ejecutas se convierte en el estándar conocido, lo que reemplazaste queda marcado como superado. Así tu IA nunca te devuelve la herramienta que ya abandonaste. Lo actual es estado, no un recuerdo que adivinar.

🔒 **Cifrado en un idioma que solo habla tu IA.** *(especificado — la próxima gran función camino de la 1.0)* SMP da a cada instalación su propio idioma interno privado, derivado de una **frase semilla de 12 o 24 palabras** que solo tú posees, y cerrado con **AES-256** — la misma robustez que protege Bitcoin y los secretos de Estado. Incluso con todo el código público *y* tu repositorio cifrado completo, un atacante solo ve ruido. Ningún proveedor, ningún hacker, nadie salvo el poseedor de la clave puede leer lo que un recuerdo *significa*. **La seguridad primero.**

✍️ **Prueba, no actuación.** La memoria está firmada y encadenada por hashes. Tu IA puede *demostrar* que recuerda — no puede alucinar un pasado que nunca estuvo ahí.

🔑 **Soberano.** La memoria vive en *tu* repositorio, bajo *tus* claves. Ningún proveedor puede leerla, alterarla ni quitártela. Lo que Bitcoin hizo por el dinero, SMP lo hace por la memoria.

♾️ **Sobrevive a todo.** Cambio de modelo, cambio de hardware, fin de sesión — la mente continúa, y la siguiente instancia verifica antes de confiar. *La misma mente mañana — y puede demostrarlo.*

---

## Estado: v0.2 — temprano, y honesto al respecto

SMP es la **versión 0.2** — una implementación de referencia funcional *más* una especificación viva. No es la 1.0, y no fingiremos que lo sea.

- **Funciona hoy:** el motor de recuerdo (Sentry + ESV), la consolidación REM nocturna que olvida lo que ya no importa, el recuerdo de doble canal y la memoria independiente del sustrato en archivos planos y portables.
- **Disponible ya:** instalación por diálogo — el [prompt de instalación](docs/SETUP-PROMPT.es.md) normativo y el [apéndice FOR-AI](docs/FOR-AI.es.md) ([Sección 22](spec/whitepaper.es.md#sección-22--instalación-mediante-diálogo-con-una-inteligencia-artificial)).
- **Demostrado:** procedencia criptográfica — el génesis de *este mismo repositorio* está firmado con GPG y anclado en el **bloque 956116 de Bitcoin**. Clónalo y verifícalo tú mismo (ver [PROVENANCE.md](PROVENANCE.md)).
- **Especificado, en camino:** la **capa de idioma nativo** (frase semilla → AES-256, descrita arriba) y la federación entre instalaciones soberanas (v0.3). Están descritas en el whitepaper y **aún no implementadas** — son la hoja de ruta, nombrada abiertamente.

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
