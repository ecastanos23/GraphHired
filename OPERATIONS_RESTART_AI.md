# Instructivo: Reiniciar servicios para aplicar nuevas variables de entorno (OpenAI)

Este documento explica los pasos que debe seguir el equipo cuando se actualiza la clave o la configuración de la IA (`OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_EMBEDDING_MODEL`) para que los servicios usen las nuevas variables.

## Resumen rápido
- Si cambias solo la variable en `.env` y no cambias imagen: reinicia contenedores.
- Si además cambias dependencias o código (p.ej. `requirements.txt`, `Dockerfile`): reconstruye las imágenes.

## Pasos (recomendado — reconstrucción completa)
1. Asegúrate de haber actualizado el archivo `.env` en la raíz con `OPENAI_API_KEY`.
2. Reconstruye y levanta los servicios (recomendado):

```bash
docker compose up -d --build
```

Este comando fuerza la reconstrucción de imágenes y los contenedores arrancarán con la nueva configuración.

## Pasos (solo reinicio de variables)
Si solo actualizaste `.env` y no hubo cambios en código/deps, alcanza con reiniciar los contenedores:

```bash
docker compose restart
```

> Nota: algunos orquestadores no recargan variables de entorno en caliente; `restart` recarga variables del contenedor del entorno del proceso padre, pero si el contenedor fue creado con variables incrustadas al build, usa `up -d --build`.

## Comprobaciones post-reinicio
- Verificar contenedores:

```bash
docker compose ps
```

- Verificar endpoint AI:

```bash
curl http://localhost:8000/health/ai
```

Salida esperada (JSON) ejemplo:

```json
{"provider":"openai","model":"gpt-4-turbo","embedding_model":"text-embedding-3-small","api_key_configured":true}
```

- Revisar logs del backend para errores:

```bash
docker compose logs -f backend
```

## Mensaje corto para pedirle a la IA/op-sysbot que reinicie
Si tu equipo usa un asistente/IA que puede ejecutar comandos, puedes enviar este prompt (cópialo y pégalo):

"Por favor, reconstruye y reinicia los servicios del proyecto GraphHired para aplicar las nuevas variables de entorno de OpenAI. Ejecuta `docker compose up -d --build`. Luego verifica `http://localhost:8000/health/ai` y confirma que `api_key_configured` sea `true`. Si hay errores, comparte los últimos 100 líneas de `docker compose logs backend`." 

## Notas para gestión de secretos
- No subas claves a repositorios públicos.
- Usa un gestor de secretos (Vault, Azure Key Vault, AWS Secrets Manager) para producción.
- Para rotación de clave: actualizar `.env` o el secreto en el gestor y luego `docker compose up -d --build`.

---
Archivo generado automáticamente por el equipo. Si quieres que lo agregue al README o cree una tarea de seguimiento en el tracker, dímelo.