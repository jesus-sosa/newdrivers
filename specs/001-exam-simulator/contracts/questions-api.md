# Contrato API: Banco de Preguntas

**Base URL**: `/api/questions`
**Autenticación**: JWT requerido en todos los endpoints. Solo roles `admin` y `editor`.

---

## GET /api/questions

Lista las preguntas del banco con soporte de paginación y filtro por tema.

**Roles permitidos**: `admin`, `editor`

**Query Parameters**:
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `tema` | string | — | Filtrar por tema exacto |
| `activa` | boolean | `true` | Filtrar por estado activa/inactiva |
| `q` | string | — | Búsqueda libre en texto de pregunta |
| `page` | integer | `1` | Página actual |
| `page_size` | integer | `20` | Resultados por página (máx. 100) |

**Response 200 OK**:
```json
{
  "total": 62,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": 1,
      "tema": "Requisitos",
      "pregunta": "¿Cuál es la edad mínima para tramitar la licencia?",
      "imagen_archivo": "imagenes_senales/pg04_img03_184x81.jpeg",
      "descripcion_imagen": "Identificación oficial mostrando mayoría de edad",
      "opcion_a": "16 años",
      "opcion_b": "17 años",
      "opcion_c": "18 años",
      "opcion_d": "21 años",
      "respuesta_correcta": "C",
      "fundamento_juridico": "Artículo 128 del RLTVY: Haber cumplido 18 años.",
      "activa": true,
      "created_at": "2026-06-17T10:00:00Z"
    }
  ],
  "temas_disponibles": ["Requisitos", "Equipos instalados", "Responsabilidad vial"]
}
```

---

## POST /api/questions

Crea una nueva pregunta en el banco.

**Roles permitidos**: `admin`, `editor`

**Request Body**:
```json
{
  "tema": "Señales restrictivas",
  "pregunta": "¿Qué indica la señal de ALTO?",
  "opcion_a": "Reducir velocidad",
  "opcion_b": "Detención total",
  "opcion_c": "Ceder el paso",
  "opcion_d": "Zona de peaje",
  "respuesta_correcta": "B",
  "imagen_archivo": "imagenes_senales/pg12_img03_68x66.jpeg",
  "descripcion_imagen": "Señal octagonal roja de ALTO",
  "fundamento_juridico": "Manual de Señalamiento SCT: La señal de ALTO indica detención total."
}
```

**Campos opcionales**: `imagen_archivo`, `descripcion_imagen`, `fundamento_juridico`

**Response 201 Created**: Objeto pregunta completo (mismo formato que ítem en GET).

**Errores**:
- `400` — campos requeridos faltantes o `respuesta_correcta` no es A/B/C/D
- `422` — validación de tipos fallida

---

## GET /api/questions/{id}

Obtiene el detalle de una pregunta específica.

**Roles permitidos**: `admin`, `editor`

**Response 200 OK**: Objeto pregunta completo.

**Errores**:
- `404` — pregunta no encontrada

---

## PUT /api/questions/{id}

Actualiza una pregunta existente.

**Roles permitidos**: `admin`, `editor`

**Request Body**: Mismos campos que POST (todos opcionales; solo se actualizan los enviados).

**Response 200 OK**: Objeto pregunta actualizado.

**Errores**:
- `404` — pregunta no encontrada
- `409` — la pregunta está en un intento activo y se intentó cambiar `respuesta_correcta`

---

## DELETE /api/questions/{id}

Desactiva (soft-delete) una pregunta.

**Roles permitidos**: `admin`, `editor`

**Comportamiento**: Establece `activa=false`. La pregunta no se elimina físicamente para preservar
la integridad de los intentos históricos.

**Response 204 No Content**

**Errores**:
- `404` — pregunta no encontrada
- `409` — la pregunta está incluida en un intento activo (no finalizado)

---

## POST /api/questions/import

Carga masiva de preguntas desde un archivo CSV.

**Roles permitidos**: `admin`, `editor`

**Request**: `multipart/form-data`
- `file`: archivo CSV con las columnas del esquema de `preguntas` (encoding UTF-8)

**Comportamiento**:
- Valida cabeceras del CSV
- Realiza `INSERT ... ON CONFLICT (id) DO UPDATE` para idempotencia
- Devuelve resumen de operación

**Response 200 OK**:
```json
{
  "insertadas": 50,
  "actualizadas": 12,
  "errores": [
    { "fila": 5, "error": "respuesta_correcta 'E' no es válida" }
  ]
}
```

**Errores**:
- `400` — archivo no proporcionado o formato inválido
- `422` — cabeceras del CSV no coinciden con el esquema esperado

---

## GET /api/questions/temas

Lista todos los temas disponibles en el banco.

**Roles permitidos**: `admin`, `editor`

**Response 200 OK**:
```json
{
  "temas": [
    "Colores de señales de tránsito",
    "Conducción segura",
    "Equipos instalados",
    "Formas de señales de tránsito",
    "Marca pavimental",
    "Requisitos",
    "Responsabilidad vial",
    "Semáforo",
    "Señales preventivas",
    "Señales restrictivas"
  ]
}
```
