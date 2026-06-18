# Especificación de Funcionalidad: Simulador de Examen de Manejo

**Rama de funcionalidad**: `001-exam-simulator`

**Creado**: 2026-06-17

**Estado**: Draft

---

## Historias de Usuario y Pruebas *(obligatorio)*

### Historia de Usuario 1 — Estudiante realiza un examen simulador (Prioridad: P1)

Un estudiante registrado en el sistema accede a la sección de examen, inicia un simulador y
responde un conjunto de preguntas de opción múltiple seleccionadas aleatoriamente del banco de
preguntas. Al finalizar, el sistema muestra el resultado indicando cuántas respuestas fueron
correctas, si aprobó o reprobó, y la retroalimentación visual por pregunta.

**Por qué esta prioridad**: Es el núcleo del producto. Sin esta historia el sistema no cumple
ningún propósito para el estudiante.

**Prueba independiente**: Se puede probar completamente iniciando sesión como estudiante, iniciando
un examen, respondiendo todas las preguntas y verificando la pantalla de resultados.

**Escenarios de Aceptación**:

1. **Dado** un estudiante autenticado en el sistema, **Cuando** inicia un nuevo examen, **Entonces**
   el sistema presenta la primera pregunta seleccionada aleatoriamente del banco, con un
   temporizador visible iniciando la cuenta regresiva de 60 segundos para esa pregunta.

2. **Dado** un estudiante respondiendo preguntas, **Cuando** selecciona una opción y avanza,
   **Entonces** la respuesta queda registrada y el progreso visual se actualiza.

3. **Dado** un estudiante que completa todas las preguntas, **Cuando** el examen finaliza
   (por envío manual o agotamiento del tiempo), **Entonces** el sistema muestra la puntuación
   obtenida (ej. "15 de 20 correctas"), indica si aprobó o reprobó, y resalta visualmente
   cada respuesta: verde para correctas, rojo para incorrectas seleccionadas, con la opción
   correcta siempre visible.

4. **Dado** un estudiante que ve sus resultados, **Cuando** selecciona "Intentar de nuevo",
   **Entonces** el sistema genera un nuevo examen con preguntas aleatorizadas.

5. **Dado** que el estudiante no responde una pregunta, **Cuando** el temporizador de 60 segundos
   de esa pregunta llega a cero, **Entonces** la pregunta se registra automáticamente como no
   respondida (incorrecta) y el sistema avanza a la siguiente pregunta sin intervención del estudiante.

6. **Dado** un estudiante que ve una pregunta con imagen de apoyo, **Cuando** la pregunta se
   presenta en pantalla, **Entonces** el sistema muestra la imagen junto al enunciado de texto.

---

### Historia de Usuario 2 — Nuevo estudiante se registra en el sistema (Prioridad: P2)

Un usuario nuevo puede crear su cuenta como estudiante para acceder al simulador.

**Por qué esta prioridad**: Es la puerta de entrada para que los estudiantes accedan al sistema
de forma autónoma.

**Prueba independiente**: Se puede verificar intentando registrar una cuenta nueva, iniciar sesión
y confirmar el acceso al simulador.

**Escenarios de Aceptación**:

1. **Dado** un usuario sin cuenta, **Cuando** completa el formulario de registro (nombre, correo
   electrónico, contraseña), **Entonces** el sistema crea su cuenta con rol de estudiante y le
   permite iniciar sesión.

2. **Dado** un usuario que intenta registrarse con un correo ya existente, **Cuando** envía el
   formulario, **Entonces** el sistema muestra un mensaje de error indicando que el correo ya
   está en uso.

3. **Dado** un estudiante recién registrado, **Cuando** inicia sesión, **Entonces** accede
   únicamente a las secciones de tomar examen e historial de resultados.

---

### Historia de Usuario 3 — Administrador y Editor gestionan el banco de preguntas (Prioridad: P3)

Un administrador o editor puede crear, editar y eliminar preguntas en el banco de preguntas
que alimenta los exámenes simuladores.

**Por qué esta prioridad**: El banco de preguntas es el contenido fundamental del sistema; sin
preguntas no hay exámenes.

**Prueba independiente**: Se puede verificar creando una nueva pregunta, editándola, y confirmando
que aparece disponible en la generación de exámenes.

**Escenarios de Aceptación**:

1. **Dado** un usuario con rol de administrador o editor, **Cuando** accede a la gestión del banco
   de preguntas, **Entonces** puede ver el listado completo de preguntas con opciones para crear,
   editar y eliminar.

2. **Dado** un editor creando una pregunta, **Cuando** ingresa el enunciado, exactamente 4 opciones
   de respuesta (A, B, C, D), la respuesta correcta, el tema al que pertenece, y opcionalmente una
   imagen de apoyo y el fundamento legal, **Entonces** la pregunta queda disponible en el banco
   para ser seleccionada en futuros exámenes.

3. **Dado** un editor que elimina una pregunta, **Cuando** confirma la eliminación, **Entonces**
   la pregunta ya no aparece en nuevos exámenes generados.

---

### Historia de Usuario 4 — Administrador configura los parámetros del examen (Prioridad: P4)

Un administrador puede definir el número de preguntas por examen, el tiempo límite y el porcentaje
de aprobación.

**Por qué esta prioridad**: Permite adaptar el simulador a los requisitos del examen oficial sin
modificar código.

**Prueba independiente**: Se puede verificar cambiando el número de preguntas a 10, generando un
examen y confirmando que solo se presentan 10 preguntas.

**Escenarios de Aceptación**:

1. **Dado** un administrador en la sección de configuración, **Cuando** modifica el número de
   preguntas por examen y guarda, **Entonces** los exámenes subsecuentes presentan exactamente
   ese número de preguntas.

2. **Dado** un administrador configurando los segundos por pregunta, **Cuando** guarda el nuevo
   valor (ej. 60 segundos), **Entonces** el temporizador de cada pregunta en futuros exámenes
   inicia con ese valor.

3. **Dado** un administrador configurando el porcentaje de aprobación, **Cuando** un estudiante
   finaliza un examen, **Entonces** el sistema determina aprobado/reprobado en base al porcentaje
   configurado.

4. **Dado** un usuario con rol de editor, **Cuando** intenta acceder a la sección de configuración,
   **Entonces** el sistema le deniega el acceso y muestra un mensaje apropiado.

---

### Historia de Usuario 5 — Administrador y Editor gestionan estudiantes (Prioridad: P5)

Un administrador o editor puede añadir nuevos estudiantes al sistema directamente, sin necesidad
de que estos se registren de forma autónoma.

**Por qué esta prioridad**: Permite que la escuela agregue estudiantes existentes de forma
administrativa.

**Prueba independiente**: Se puede verificar creando un estudiante desde el panel administrativo
e iniciando sesión con sus credenciales.

**Escenarios de Aceptación**:

1. **Dado** un administrador o editor en la sección de estudiantes, **Cuando** ingresa los datos
   del nuevo estudiante (nombre, correo, contraseña temporal), **Entonces** la cuenta queda creada
   con rol de estudiante.

2. **Dado** un administrador, **Cuando** busca o lista los estudiantes registrados, **Entonces**
   puede ver el historial de exámenes de cada uno incluyendo puntuaciones y fechas.

---

### Historia de Usuario 6 — Estudiante consulta su historial de resultados (Prioridad: P6)

Un estudiante puede revisar los resultados de sus exámenes anteriores.

**Por qué esta prioridad**: Permite al estudiante hacer seguimiento de su progreso.

**Prueba independiente**: Completar al menos dos exámenes y verificar que ambos aparecen en
el historial con sus respectivas puntuaciones.

**Escenarios de Aceptación**:

1. **Dado** un estudiante autenticado, **Cuando** accede a su historial, **Entonces** ve la lista
   de todos sus intentos con fecha, puntuación obtenida y resultado (aprobado/reprobado).

2. **Dado** un estudiante consultando un intento pasado, **Cuando** selecciona ver el detalle,
   **Entonces** puede revisar pregunta por pregunta su respuesta y la respuesta correcta.

---

### Casos Borde

- ¿Qué ocurre si el banco de preguntas tiene menos preguntas que el número configurado para el examen?
  El sistema DEBE mostrar un error al administrador y no permitir iniciar exámenes hasta que haya
  suficientes preguntas.
- ¿Qué ocurre si el estudiante pierde la conexión durante el examen? Las respuestas guardadas hasta
  ese momento se conservan; al reconectarse el temporizador continúa desde donde estaba.
- ¿Qué pasa si un estudiante intenta acceder a la configuración directamente por URL? El sistema
  deniega el acceso independientemente de la navegación.

---

## Requisitos *(obligatorio)*

### Requisitos Funcionales

**Autenticación y Control de Acceso**

- **RF-001**: El sistema DEBE permitir a usuarios nuevos registrarse como estudiantes con nombre,
  correo electrónico y contraseña.
- **RF-002**: El sistema DEBE autenticar a los usuarios con correo y contraseña.
- **RF-003**: El sistema DEBE implementar control de acceso basado en roles (RBAC) con tres
  roles: `admin`, `editor` y `estudiante`.
- **RF-004**: El sistema DEBE restringir el acceso a la sección de configuración únicamente al
  rol `admin`.
- **RF-005**: El rol `editor` DEBE tener acceso a gestión del banco de preguntas y gestión de
  estudiantes, pero NO a la sección de configuración del sistema.
- **RF-006**: El rol `estudiante` DEBE tener acceso únicamente a la sección de tomar examen y
  su historial de resultados.

**Banco de Preguntas**

- **RF-007**: El sistema DEBE permitir a administradores y editores crear preguntas con: enunciado,
  exactamente 4 opciones de respuesta (A, B, C, D), indicador de la opción correcta, tema de
  clasificación, imagen de apoyo (opcional) y fundamento legal (opcional).
- **RF-008**: El sistema DEBE permitir a administradores y editores editar y eliminar preguntas
  existentes. Una pregunta no puede eliminarse si está incluida en un intento de examen activo.
- **RF-009**: El sistema DEBE proporcionar un mecanismo de carga masiva del banco de preguntas
  existente desde un archivo estructurado.
- **RF-009a**: El sistema DEBE organizar las preguntas por tema y permitir filtrar el banco de
  preguntas por tema desde el panel administrativo.
- **RF-009b**: Cuando una pregunta tenga imagen de apoyo, el sistema DEBE mostrar dicha imagen
  junto al enunciado durante el examen.

**Generación de Exámenes**

- **RF-010**: El sistema DEBE generar cada examen seleccionando aleatoriamente el número de
  preguntas configurado del banco de preguntas disponible.
- **RF-011**: El sistema DEBE mostrar un temporizador visible por pregunta que inicia la cuenta
  regresiva configurada (default 60 segundos) al presentarse cada nueva pregunta.
- **RF-012**: Cuando el temporizador de una pregunta llega a cero, el sistema DEBE registrar
  automáticamente la pregunta como no respondida y avanzar a la siguiente sin intervención del
  estudiante.
- **RF-013**: El sistema DEBE mostrar el progreso del estudiante durante el examen (ej. pregunta
  3 de 20).

**Resultados**

- **RF-014**: Al finalizar el examen, el sistema DEBE mostrar la puntuación total (X de N correctas).
- **RF-015**: El sistema DEBE indicar claramente si el estudiante aprobó o reprobó, en base al
  porcentaje de aprobación configurado.
- **RF-016**: El sistema DEBE mostrar retroalimentación visual por pregunta: respuesta correcta
  en verde, respuesta incorrecta seleccionada en rojo, y para preguntas no respondidas (tiempo
  agotado) DEBE indicar cuál era la respuesta correcta.
- **RF-016a**: En la pantalla de resultados, el sistema DEBE mostrar el fundamento legal o
  explicación de cada pregunta, para facilitar el aprendizaje del estudiante.
- **RF-017**: El sistema DEBE permitir al estudiante iniciar un nuevo intento desde la pantalla
  de resultados.
- **RF-018**: El sistema DEBE guardar cada intento en el historial del estudiante.

**Configuración del Sistema (solo admin)**

- **RF-019**: El sistema DEBE permitir al administrador configurar el número de preguntas por examen.
- **RF-020**: El sistema DEBE permitir al administrador configurar la duración del temporizador
  por pregunta en segundos.
- **RF-021**: El sistema DEBE permitir al administrador configurar el porcentaje mínimo de
  respuestas correctas para aprobar, con un rango válido de 0% a 100% (incluyendo 100% para
  exámenes de pocas preguntas donde se exige perfección). El sistema DEBE requerir que este
  valor esté explícitamente configurado antes de activar los exámenes.

**Gestión de Estudiantes**

- **RF-022**: El sistema DEBE permitir a administradores y editores crear cuentas de estudiantes
  directamente desde el panel administrativo.
- **RF-023**: El sistema DEBE permitir al administrador ver el historial de exámenes de cualquier
  estudiante registrado.

### Entidades Clave

- **Usuario**: Representa a cualquier persona con acceso al sistema. Atributos: nombre completo,
  correo electrónico, contraseña (cifrada), rol, fecha de registro, estado (activo/inactivo).
- **Rol**: Define el nivel de acceso. Valores fijos: `admin`, `editor`, `estudiante`.
- **Pregunta**: Unidad del banco de preguntas. Atributos: enunciado (texto), tema/categoría,
  exactamente 4 opciones de respuesta (A, B, C, D), indicador de la opción correcta, imagen de
  apoyo (opcional), fundamento legal o explicación (opcional).
- **ConfiguraciónExamen**: Parámetros globales del simulador. Atributos: número de preguntas por
  examen, duración del temporizador por pregunta (segundos), porcentaje mínimo de aprobación.
- **IntentoExamen**: Registro de una sesión de examen de un estudiante. Atributos: estudiante,
  preguntas presentadas, opción seleccionada por pregunta (puede ser vacía si el tiempo se agotó),
  puntuación final, resultado (aprobado/reprobado), fecha y hora de inicio y fin.

---

## Criterios de Éxito *(obligatorio)*

### Resultados Medibles

- **CE-001**: Un estudiante puede completar un examen simulador de principio a fin en menos de
  30 minutos desde que inicia sesión por primera vez.
- **CE-002**: El sistema genera exámenes con preguntas no repetidas dentro del mismo intento
  en el 100% de los casos.
- **CE-003**: El resultado del examen (aprobado/reprobado y puntuación) se presenta al estudiante
  en menos de 3 segundos tras finalizar.
- **CE-004**: El 100% de los intentos de examen quedan registrados en el historial del estudiante
  sin pérdida de datos.
- **CE-005**: Un administrador puede modificar la configuración del examen y ver los cambios
  reflejados en el siguiente intento generado, sin intervención técnica.
- **CE-006**: Un editor puede añadir una nueva pregunta al banco y esta quede disponible para
  nuevos exámenes en menos de 1 minuto.
- **CE-007**: El control de acceso por roles funciona correctamente en el 100% de las rutas del
  sistema — ningún rol accede a secciones fuera de sus permisos.

---

## Supuestos

- Las preguntas del banco son de opción múltiple con una sola respuesta correcta (no selección
  múltiple), consistente con las capturas de pantalla de referencia.
- Las preguntas se presentan de forma paginada durante el examen (no todas en una sola página de
  scroll), con un botón "Continuar" para avanzar al siguiente grupo, tal como muestran las imágenes
  de referencia.
- La identidad visual del simulador sigue el branding de New Drivers: fondo oscuro en barra
  superior, tipografía negra, botones y respuestas correctas en verde, respuestas incorrectas en
  rojo, conforme a las imágenes compartidas.
- El registro de nuevos estudiantes es abierto (cualquier persona puede crear una cuenta con rol
  de estudiante); los roles de admin y editor solo son asignables por un administrador existente.
- El banco de preguntas inicial está disponible en formato digital estructurado y listo para ser
  importado al sistema; el mecanismo de importación será definido en la fase de planificación técnica.
- El simulador es un sistema web, accesible desde navegador de escritorio y móvil.
- Un solo conjunto de configuración aplica a todos los exámenes generados (no hay múltiples
  "tipos" de examen con configuraciones distintas en esta versión).
- El idioma de la interfaz es español.
