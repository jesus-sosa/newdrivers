# Contrato API: Autenticación y Registro

**Base URL**: `/api/auth`
**Autenticación**: Los endpoints de este grupo son públicos (sin JWT requerido), excepto `GET /me`.

---

## POST /api/auth/register

Crea una nueva cuenta de estudiante de forma autónoma.

**Roles permitidos**: Público (sin autenticación)

**Request Body**:
```json
{
  "nombre_completo": "Juan Pérez García",
  "email": "juan@example.com",
  "password": "contraseña_segura_123"
}
```

**Validaciones**:
- `email`: formato válido, único en el sistema
- `password`: mínimo 8 caracteres
- `nombre_completo`: requerido, 2–255 caracteres

**Response 201 Created**:
```json
{
  "id": "uuid",
  "nombre_completo": "Juan Pérez García",
  "email": "juan@example.com",
  "rol": "estudiante"
}
```

**Errores**:
- `400` — validación de campos fallida
- `409` — email ya registrado

---

## POST /api/auth/login

Autentica al usuario y devuelve tokens JWT.

**Roles permitidos**: Público

**Request Body**:
```json
{
  "email": "juan@example.com",
  "password": "contraseña_segura_123"
}
```

**Response 200 OK**:
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "nombre_completo": "Juan Pérez García",
    "email": "juan@example.com",
    "rol": "estudiante"
  }
}
```

El `refresh_token` se establece como cookie httpOnly (`Set-Cookie: refresh_token=...; HttpOnly; Secure; SameSite=Strict`).

**Errores**:
- `401` — credenciales inválidas
- `403` — cuenta inactiva

---

## POST /api/auth/refresh

Renueva el access token usando el refresh token de la cookie.

**Roles permitidos**: Público (usa cookie httpOnly)

**Request**: Sin body. El refresh token se lee desde la cookie.

**Response 200 OK**:
```json
{
  "access_token": "<nuevo_jwt>",
  "token_type": "bearer"
}
```

**Errores**:
- `401` — refresh token ausente, inválido o expirado

---

## POST /api/auth/logout

Invalida el refresh token.

**Roles permitidos**: Cualquier usuario autenticado

**Headers**: `Authorization: Bearer <access_token>`

**Response 204 No Content**

Elimina la cookie `refresh_token` (Set-Cookie con `expires` en el pasado).

---

## GET /api/auth/me

Devuelve los datos del usuario autenticado actualmente.

**Roles permitidos**: Cualquier usuario autenticado

**Headers**: `Authorization: Bearer <access_token>`

**Response 200 OK**:
```json
{
  "id": "uuid",
  "nombre_completo": "Juan Pérez García",
  "email": "juan@example.com",
  "rol": "estudiante",
  "activo": true,
  "created_at": "2026-06-17T10:00:00Z"
}
```

**Errores**:
- `401` — token ausente o inválido
