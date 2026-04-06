# http-llm-echo

Flujo n8n que expone un webhook HTTP y devuelve un "eco" de un LLM usando el mensaje recibido en el body. La respuesta contiene el texto de entrada y la respuesta del modelo.

## Resumen del flujo

1. Recibe una peticion HTTP `POST` en `/webhook/llm-test`.
2. Extrae `body.message` y agrega una marca de tiempo.
3. Envia el mensaje al modelo `gpt-4o-mini`.
4. Responde al webhook con un JSON que incluye el input y la respuesta del modelo.

## Nodos y configuracion

### 1) Webhook

- Tipo: `n8n-nodes-base.webhook`
- Metodo: `POST`
- Path: `llm-test`
- Response mode: `responseNode` (la respuesta la construye el nodo "Respond to Webhook").

Entrada esperada (ejemplo):

```json
{
  "message": "Explicame que es n8n en una frase?"
}
```

### 2) Edit Fields

- Tipo: `n8n-nodes-base.set`
- Objetivo: normalizar la entrada y agregar timestamp.

Campos configurados:

- `message`: se copia de `{{$json.body.message}}`.
- `receivedAt`: se establece a `{{$now}}`.

### 3) Message a model

- Tipo: `@n8n/n8n-nodes-langchain.openAi`
- Modelo: `gpt-4o-mini`
- Entrada del modelo: `{{ $json.message }}`.
- Reintentos: `2` con `5000ms` de espera.

Resultado esperado:

- El nodo devuelve la salida del modelo como `output[0].content[0].text`.

### 4) Respond to Webhook

- Tipo: `n8n-nodes-base.respondToWebhook`
- Formato: JSON

Cuerpo de respuesta:

```json
{
  "input": "{{$node['Edit Fields'].json.message}}",
  "llm_response": "{{ $json.output[0].content[0].text }}"
}
```

## Datos de prueba (pinData)

El JSON incluye `pinData` con un ejemplo de request. Esto es util para pruebas locales, pero en un repo publico conviene limpiarlo si contiene datos sensibles (por ejemplo IPs o URLs de un VPS).

## Seguridad y publicacion

Recomendaciones para publicar:

- Quitar `pinData` si contiene IPs, URLs, headers, o payloads reales.
- Evitar publicar identificadores de credenciales (`credentials.openAiApi.id`) si no es necesario.
- Evitar publicar `meta.instanceId` y otros metadatos de instancia.

Si quieres, puedo generar una version "sanitizada" del flujo para subirlo a GitHub.
