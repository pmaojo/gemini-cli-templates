# Guía de Workflow: Ralph Wiggum + Architect

Este documento describe el flujo de trabajo completo ("End-to-End") para el desarrollo de software agéntico utilizando el patrón Ralph Wiggum.

## Resumen del Flujo

1.  **Entrevista (Architect)**: Definición de requerimientos asistida por IA.
2.  **Revisión (Humano)**: Verificación y ajuste del Spec.
3.  **Ejecución (Ralph Loop)**: Desarrollo iterativo y autónomo.
4.  **Validación**: Confirmación final.

---

## Paso 1: Entrevista con el Arquitecto

En lugar de escribir un prompt gigante, deja que el Arquitecto te entreviste para construir un `SPECS.md` robusto.

```bash
# Inicia la sesión de entrevista
./cli-tool/components/skills/development/ralph-wiggum/scripts/architect.sh
```

**Qué sucede:**
*   El agente te preguntará: "¿Qué quieres construir?"
*   Te hará preguntas sobre tecnologías, casos de uso y limitaciones.
*   Al finalizar, generará un archivo `SPECS.md` en el directorio actual.

## Paso 2: Revisión y Notion (Opcional)

Si prefieres colaborar o guardar el Spec en Notion:

```bash
# Sube el Spec generado a Notion (Requiere configuración previa)
./cli-tool/components/skills/development/ralph-wiggum/scripts/notion-sync.sh push
```

O simplemente edita el archivo `SPECS.md` localmente con tu editor favorito:

```bash
code SPECS.md
```

**Asegúrate de que el Spec incluya:**
*   Comandos de prueba claros (e.g., `npm test`).
*   Requisitos funcionales explícitos.

## Paso 3: Ejecución "Ralph Loop" (AFK Mode)

Una vez que tienes el `SPECS.md` y un comando de verificación (tests), lanza a Ralph. Él leerá el Spec y trabajará hasta que los tests pasen.

```bash
# Lanza el loop
./cli-tool/components/skills/development/ralph-wiggum/scripts/ralph.sh \
  --spec SPECS.md \
  --verify "npm test" \
  --max-iter 20 \
  --afk
```

**El ciclo de Ralph:**
1.  **Lee** el `SPECS.md` y el estado actual del código.
2.  **Escribe** código.
3.  **Ejecuta** `npm test`.
4.  **Si falla**: Lee el error, lo analiza y vuelve al paso 2 (Nueva Iteración).
5.  **Si pasa**: Hace commit (`git commit`) y termina.

## Paso 4: Validación Final

Cuando Ralph termina (porque los tests pasaron), revisa el trabajo.

```bash
git log -1
# Deberías ver: "Ralph: Task completed (Iter X)"
```

¡Disfruta de tu software construido automáticamente!
