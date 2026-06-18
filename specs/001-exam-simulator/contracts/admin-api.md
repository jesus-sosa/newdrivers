# Contrato API: Administración

**Base URL**: `/api/admin`
**Autenticación**: JWT requerido. Roles indicados por endpoint.

---

## GET /api/admin/config

Obtiene la configuración actual del simulador.

**Roles permitidos**: `admin`

**Response 200 OK**:
```json
{
  "num_preguntas": 20,
  "segundos_por_pregunta": 60,
  "porcentaje_aprobacion": null,
  "updated_at": null,
  "updated_by": null,
  "estado_sistema": "no_configurado"
}
```

`estado_sistema`:
- `"no_configurado"` — `porcentaje_aprobacion` es null; los exámenes no pueden iniciarse
- `"activo"` — configuración completa; los exámenes pueden iniciarse

**Errores**:
- `403` — rol no permitido

---

## PUT /api/admin/config

Actualiza la configuración del simulador.

**Roles permitidos**: `admin`

**Request Body** (todos los campos opcionales; solo se actualizan los enviados):
```json
{
  "num_preguntas": 20,
  "segundos_por_pregunta": 60,
  "porcentaje_aprobacion": 70.0
}
```

**Validaciones**:
- `num_preguntas`: entero > 0; no puede ser mayor al total de preguntas activas en el banco
- `segundos_por_pregunta`: entero > 0
- `porcentaje_aprobacion`: decimal 0.0–100.0

**Response 200 OK**: Objeto de configuración completo (mismo formato que GET).

**Errores**:
- `400` — validación fallida (ej. `num_preguntas` mayor al banco disponible)
- `403` — rol no permitido

---

## GET /api/admin/students

Lista los estudiantes registrados en el sistema.

**Roles permitidos**: `admin`, `editor`

**Query Parameters**:
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `q` | string | — | Búsqueda por nombre o email |
| `activo` | boolean | `true` | Filtrar por estado |
| `page` | integer | `1` | Página |
| `page_size` | integer | `20` | Resultados por página |

**Response 200 OK**:
```json
{
  "total": 45,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": "uuid",
      "nombre_completo": "Juan Pérez García",
      "email": "juan@example.com",
      "activo": true,
      "created_at": "2026-06-17T10:00:00Z",
      "total_intentos": 3,
      "ultimo_resultado": "aprobado"
    }
  ]
}
```

---

## POST /api/admin/students

Crea una cuenta de estudiante directamente desde el panel administrativo.

**Roles permitidos**: `admin`, `editor`

**Request Body**:
```json
{
  "nombre_completo": "María López Sánchez",
  "email": "maria@example.com",
  "password": "temporal_123"
}
```

**Comportamiento**: Crea el usuario con `rol=estudiante`. La contraseña es temporal; el
estudiante puede cambiarla en futuras versiones.

**Response 201 Created**:
```json
{
  "id": "uuid",
  "nombre_completo": "María López Sánchez",
  "email": "maria@example.com",
  "rol": "estudiante",
  "activo": true,
  "created_at": "2026-06-17T10:00:00Z"
}
```

**Errores**:
- `409` — email ya registrado
- `403` — rol no permitido

---

## GET /api/admin/students/{id}

Obtiene el detalle de un estudiante específico con su historial de exámenes.

**Roles permitidos**: `admin`

**Response 200 OK**:
```json
{
  "id": "uuid",
  "nombre_completo": "Juan Pérez García",
  "email": "juan@example.com",
  "activo": true,
  "created_at": "2026-06-17T10:00:00Z",
  "intentos": [
    {
      "attempt_id": "uuid",
      "iniciado_at": "2026-06-17T10:00:00Z",
      "finalizado_at": "2026-06-17T10:18:32Z",
      "puntuacion": 15,
      "total_preguntas": 20,
      "resultado": "aprobado"
    }
  ]
}
```

**Errores**:
- `404` — estudiante no encontrado
- `403` — rol no permitido

---

## PATCH /api/admin/students/{id}/status

Activa o desactiva la cuenta de un estudiante.

**Roles permitidos**: `admin`

**Request Body**:
```json
{
  "activo": false
}
```

**Response 200 OK**: Objeto usuario actualizado.

**Errores**:
- `404` — estudiante no encontrado
- `403` — rol no permitido
- `400` — intento de desactivar la propia cuenta
