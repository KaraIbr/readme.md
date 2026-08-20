# Model Test

Aplicación Streamlit para probar y comparar modelos LLM hospedados en Azure (Azure OpenAI / Azure AI Foundry).

Modelos incluidos por ahora:

| Modelo | Recurso Azure | API |
|--------|---------------|-----|
| GPT-5.6 Sol | `chatiq.openai.azure.com` | Responses |
| GPT-5.6 Terra | `chatiq.openai.azure.com` | Responses |
| DeepSeek V4 Pro | Azure AI Services | Chat Completions |
| Grok 4.3 | Azure AI Services | Chat Completions |

---

## Requisitos

- [uv](https://docs.astral.sh/uv/) instalado
- Python 3.14 (el proyecto lo gestiona con uv)
- Acceso a los recursos Azure y sus API keys

---

## 1. Configuración inicial

### 1.1 Clonar / abrir el proyecto

```bash
cd modeltest
```

### 1.2 Instalar dependencias

```bash
uv sync
```

Esto crea el entorno virtual e instala las librerías de runtime y de desarrollo (Ruff, pytest).

### 1.3 Crear el archivo `.env`

Copia el ejemplo y completa las keys:

```bash
cp .env.example .env
```

Edita `.env` con tus valores. Las variables importantes son:

```env
# Recurso Azure OpenAI (GPT)
AZURE_OPENAI_ENDPOINT=https://chatiq.openai.azure.com
AZURE_OPENAI_API_VERSION=2025-04-01-preview
AZURE_OPENAI_API_KEY=pega-aqui-la-key-de-chatiq

# Recurso Azure AI (DeepSeek / Grok)
AZURE_AI_ENDPOINT=https://ai-asigcha5956ai083120569258.services.ai.azure.com
AZURE_AI_API_VERSION=2024-05-01-preview
AZURE_AI_API_KEY=pega-aqui-la-key-del-recurso-ai
```

Notas:

- Cada recurso suele tener su propia key. No mezcles la de `chatiq` con la del recurso AI.
- Copia la key desde **Azure Portal → recurso → Keys and Endpoint**.
- Si en el portal el deployment se llama distinto, ajusta las variables `DEPLOYMENT_*`.
- El archivo `.env` no se sube a git (está en `.gitignore`).

Opcional — smoke test de GPT sin abrir la UI:

```bash
uv run python main.py
```

---

## 2. Ejecutar la aplicación

```bash
uv run streamlit run app.py
```

Abre en el navegador la URL que indique Streamlit (normalmente [http://localhost:8501](http://localhost:8501)).

Para detenerla: `Ctrl+C` en la terminal.

---

## 3. Uso de la interfaz

### 3.1 Selección de modelo (barra lateral)

En **Modelo** elige cuál quieres probar. Al cambiar de modelo se actualizan:

- El deployment asociado
- El tipo de API / backend
- Los parámetros disponibles (sobre todo el nivel de razonamiento)

### 3.2 Parámetros

#### Razonamiento

Controla cuánto “piensa” el modelo antes de responder. **Las opciones dependen del modelo seleccionado**:

| Modelo | Opciones | Default |
|--------|----------|---------|
| GPT-5.6 Sol / Terra | Bajo · Medio · Alto | Medio |
| DeepSeek V4 Pro | Sin razonamiento · Alto · Máximo | Alto |
| Grok 4.3 | Ninguno · Bajo · Medio · Alto | Bajo |

Niveles más altos suelen mejorar calidad en tareas difíciles, a costa de más latencia y tokens.

Temperature y Top P no se muestran: estos modelos de razonamiento no los usan (o los ignoran).

#### Max output tokens

Límite máximo de tokens en la respuesta. Default típico: `4096`.  
Para razonamiento alto conviene no bajarlo demasiado: parte del presupuesto se usa en pensamiento interno.

#### System prompt (opcional)

Instrucciones de sistema que se envían junto con el prompt del usuario, por ejemplo:

```text
Eres un asistente experto en análisis financiero.
Responde en español, de forma concisa y con viñetas.
```

Si lo dejas vacío, no se envía mensaje de sistema.

### 3.3 Prompt

En el área principal escribe la pregunta o tarea. Es obligatorio para poder enviar.

### 3.4 Documento u imagen (opcional)

Puedes anexar **un** archivo:

- PDF
- Imágenes: PNG, JPEG, WEBP, GIF

Comportamiento:

- **GPT**: PDF e imágenes se envían de forma nativa cuando el modelo lo soporta.
- **DeepSeek**: sin visión; el PDF se envía como texto extraído (verás un aviso).
- **Grok**: imágenes nativas; PDF como texto extraído.

### 3.5 Enviar y ver la respuesta

1. Pulsa **Enviar**.
2. Espera el spinner mientras se consulta Azure.
3. La respuesta aparece en markdown debajo.
4. Si hubo degradaciones (p. ej. PDF como texto), se muestran como avisos amarillos.

---

## 4. Flujo recomendado para una prueba

1. Elige el modelo (p. ej. GPT-5.6 Sol).
2. Deja razonamiento en **Medio** (o el default del modelo).
3. Opcional: escribe un system prompt corto.
4. Escribe un prompt claro y acotado.
5. Opcional: adjunta un PDF o imagen relevante.
6. Envía y revisa la respuesta.
7. Cambia modelo y/o nivel de razonamiento y repite con el mismo prompt para comparar.

---

## 5. Estructura del proyecto

```text
modeltest/
├── app.py                 # Entrypoint Streamlit
├── main.py                # Smoke test rápido (GPT vía .env)
├── .env                   # Secretos locales (no versionado)
├── .env.example           # Plantilla de configuración
├── src/
│   ├── config/            # Settings y catálogo de modelos
│   ├── documents/         # Preparación de PDF / imágenes
│   └── models/            # Clientes Azure + providers
├── ui/                    # Sidebar y estilos
└── tests/                 # Pruebas unitarias
```

Para agregar un modelo nuevo en el futuro: registra el spec en `src/config/settings.py` (deployment, API, capacidades y opciones de razonamiento) y, si hace falta, ajusta el provider en `src/models/`.

---

## 6. Desarrollo

Lint / formato:

```bash
uv run ruff check src ui app.py tests
uv run ruff format src ui app.py tests
```

Tests:

```bash
uv run pytest
```

---

## 7. Problemas frecuentes

### Error 401 (Access denied / invalid subscription key)

- Revisa que la key sea del **mismo recurso** que el endpoint.
- Regenera la key en el portal y actualiza `.env`.
- Evita tener una `AZURE_OPENAI_API_KEY` vieja exportada en la terminal: la app fuerza la lectura del `.env` con `override=True`, pero conviene no mezclar valores en el shell.

### El playground de Azure funciona pero la app no

El playground a menudo usa tu sesión (Entra ID). La app usa API key. Confirma Keys and Endpoint del recurso correcto.

### PDF no se “entiende” bien

Si el modelo no soporta PDF nativo, se extrae texto con `pypdf`. PDFs escaneados (solo imagen) pueden salir vacíos; en ese caso usa una captura/imagen o un modelo con visión + PDF nativo (GPT).

### Cambié el `.env` y no se refleja

Reinicia Streamlit (`Ctrl+C` y vuelve a `uv run streamlit run app.py`).
