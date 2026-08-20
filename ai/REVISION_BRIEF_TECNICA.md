# Revisión de Brief y Técnica — Ventura Energy Software

**Fecha:** 29 de abril de 2026
**Documento:** Revisión de Requisitos y Planificación Técnica
**Estado:** Draft v1.0

---

## 1. Contexto General

### 1.1 Empresa
**Ventura Energy** es una empresa líder en el sector de **energías eléctricas y renovables**.

### 1.2 Iniciativa
Desarrollo de un software interno de gestión operacional con proyección a **Software as a Service (SaaS)** como nuevo modelo de negocio.

### 1.3 Stakeholders Clave

| Rol | Nombre |
|---|---|
| Product Owner | Héctor |
| Líder del Proyecto | Karina Ibarra |
| Software Architect | Semi-Senior |
| Desarrolladores | 2 expertos en formación |

### 1.4 Cliente Principal
Ventura Energy (primer cliente y validador del MVP).

---

## 2. Alcance del Sistema

### 2.1 Visión
Sistema integral modular diseñado para escalar a SaaS y brindarse a empresas del sector energético.

### 2.2 MVP: CRM Comercial

#### 2.2.1 Objetivo
Generar **trazabilidad completa** en el área comercial de Ventura Energy, con estándar de CRMs profesionales adaptado al negocio.

#### 2.2.2 Referente Principal
**HubSpot** — como benchmark de funcionalidades y experiencia de usuario.

#### 2.2.3 Funcionalidades del CRM

| Módulo | Descripción |
|---|---|
| **Registro de Empresas** | Clientes, contactos, medios de contacto, tamaño de empresa, sector, ubicación |
| **Seguimiento al Cliente** | Llamadas, revisiones de clientes congelados, razones de pérdida, satisfacción |
| **Visitas Técnicas** | Opcionales — si requiere visita, genera agenda automáticamente |
| **Cotizaciones** | Prospecto → Cotización formal → Crédito. Actualización mensual con fecha de vencimiento. Versionado de cotizaciones |
| **Sistema de Atracción B2B** | Pipeline de captación de clientes corporativos |

#### 2.2.4 Entidades del CRM

- **Empresa:** nombre, tamaño, sector, ubicación, intereses
- **Contacto:** datos de contacto, medios de comunicación, relación con empresa
- **Oportunidad/Prospecto:** estado en pipeline, cotización asociada
- **Cotización:** versión, fecha de emisión, fecha de vencimiento, monto
- **Interacción:** llamadas, visitas, notas de satisfacción
- **Visita Técnica:** fecha, propósito, estado, agenda

#### 2.2.5 Out of Scope (NO incluido en MVP)

- BOM (Bill of Materials)
- Soporte técnico
- Administración contable
- Gestión de créditos
- Project Management (PM)

---

## 3. Alineación Estratégica

### 3.1 Objetivos por Fechas
*Por definir — requiere planificación con Product Owner.*

> **Nota:** Este documento no incluye estimaciones de tiempo ni coste.

### 3.2 Roadmap de Alto Nivel

| Fase | Entregable |
|---|---|
| **Fase 1 (MVP)** | CRM Comercial — trazabilidad completa |
| **Fase 2** | Módulos operacionales adicionales |
| **Fase 3** | Multi-tenant y preparación SaaS |
| **Fase 4** | Comercialización externa |

---

## 4. Stack Tecnológico

### 4.1 Infraestructura

| Componente | Tecnología |
|---|---|
| Cloud Provider | Google Cloud Platform |
| Servidores | Linux |
| Base de Datos | PostgreSQL / SQL Server / MariaDB *(por definir)* |

### 4.2 Frontend

| Componente | Tecnología |
|---|---|
| Framework | React |
| Design System | Existente (optimizado) |

### 4.3 Backend
*Por definir — se recomienda Node.js, Python o Go según experiencia del equipo.*

### 4.4 Herramientas Adicionales

- Modelo de IA integrado (detalles por especificar)
- Automatización de pruebas

---

## 5. Metodologías

### 5.1 Design Thinking
- Enfocado en la experiencia del usuario comercial
- Validación continua con stakeholders de Ventura Energy

### 5.2 Scrum
- Sprints iterativos
- Roles definidos: PO (Héctor), Líder (Karina), Equipo de desarrollo
- Ceremonias: planning, daily, review, retrospective

### 5.3 Agile
- Entrega incremental
- Priorización basada en valor de negocio

---

## 6. Estándares de Calidad

### 6.1 Testing
- Automatización de pruebas implementada
- Cobertura mínima por definir
- CI/CD pipeline por configurar

### 6.2 Código
- Code reviews obligatorios
- Convenciones de código documentadas
- Arquitectura modular

### 6.3 Diseño
- Design system existente
- UX optimizado
- Accesibilidad por considerar

### 6.4 Seguridad
- Autenticación y autorización
- Protección de datos de clientes
- Backups y disaster recovery

---

## 7. Plan de Acción

### 7.1 Fases Inmediatas

| # | Acción | Responsable | Estado |
|---|---|---|---|
| 1 | Definir arquitectura técnica detallada | Arquitecto | Pendiente |
| 2 | Especificar requisitos funcionales del CRM | PO (Héctor) + Equipo | Pendiente |
| 3 | Diseñar wireframes y flujos de usuario | Diseño | Pendiente |
| 4 | Configurar infraestructura en GCP | Arquitecto | Pendiente |
| 5 | Definir esquema de base de datos | Arquitecto + Backend | Pendiente |
| 6 | Sprint 0 — Setup del proyecto | Equipo | Pendiente |
| 7 | Desarrollo MVP CRM | Equipo | Pendiente |

### 7.2 Próximas Decisiones

1. **Base de datos definitiva:** seleccionar entre PostgreSQL, SQL Server o MariaDB
2. **Tecnología de backend:** definir framework y lenguaje
3. **Cronograma:** establecer objetivos por fechas con PO
4. **Modelo de IA:** definir caso de uso específico dentro del CRM
5. **Estrategia multi-tenant:** planificar arquitectura para SaaS

---

## 8. Riesgos Identificados

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Equipo en formación | Medio | Mentoring del arquitecto, pair programming |
| Scope creep | Alto | Definición clara de in/out of scope, backlog priorizado |
| Falta de cronograma | Alto | Establecer hitos con PO en próxima sesión |
| Escalabilidad a SaaS | Medio | Arquitectura modular desde el inicio |

---

## 9. Recomendaciones

1. **Definir backend** lo antes posible para no bloquear desarrollo
2. **PostgreSQL** como recomendación de BD por compatibilidad con GCP y ecosistema
3. **Establecer métricas de éxito** del CRM (adopción, conversión, satisfacción)
4. **Documentar design system** para mantener consistencia
5. **Planificar estrategia de datos** para multi-tenant desde Fase 1
6. **Integrar IA** en funcionalidades concretas: scoring de prospectos, predicción de cierre, análisis de satisfacción

---

## 10. Glosario

| Término | Definición |
|---|---|
| CRM | Customer Relationship Management |
| MVP | Minimum Viable Product |
| SaaS | Software as a Service |
| B2B | Business to Business |
| BOM | Bill of Materials |
| PO | Product Owner |
| GCP | Google Cloud Platform |

---

*Documento generado como revisión de brief y técnica. Requiere validación por Product Owner (Héctor) y Líder de Proyecto (Karina Ibarra).*


Campos de la Tabla actualmente en Notion 
Status

Added

Tipo de Proyecto

Account Owner

Last Contact

Promotor

Corrida Financiera

Priority

Ciudad

Estimated Value

Company

Email

Expected Close

Phone

Cotización

Modulacion

Contacto

Recibo CFE

Contrato

Fotos GPS

Actividad









🔴 Problemas Críticos Identificados
1. Decisiones bloqueantes sin resolver
Tres elementos pueden frenar el desarrollo desde el día 1:

Backend sin definir — sin esto, no se puede diseñar la API ni la arquitectura de servicios
Base de datos sin confirmar — afecta el esquema, migraciones y estrategia multi-tenant futura
Sin cronograma — el equipo no tiene norte claro; el riesgo de scope creep se activa desde Sprint 0

2. Las entidades del CRM no coinciden con los campos reales
El brief define entidades teóricas, pero los campos actuales de Notion revelan lo que el equipo realmente usa hoy. Hay campos en Notion que no están mapeados en ninguna entidad del brief:
Campo en Notion¿Está en el brief?AcciónStatus✅ (pipeline)OKPromotor❌Agregar a Contacto u OportunidadCorrida Financiera❌¿Es parte de Cotización? DefinirModulación❌¿Producto solar? Requiere clarificaciónRecibo CFE❌Documento adjunto — definir entidadFotos GPS❌Relacionado a Visita TécnicaContrato❌¿Post-cotización? Fuera de MVP o noCorrida Financiera❌Podría ser cálculo interno de cotización

⚠️ Acción urgente: Validar con Héctor (PO) si Corrida Financiera, Modulación, Recibo CFE y Contrato entran al MVP o se posponen.

3. El scope del MVP es ambiguo en el límite con Fase 2
Está bien definido lo que no entra (BOM, contabilidad, PM), pero no está claro cuándo termina el MVP. No hay criterio de "done" para la Fase 1.

🟡 Observaciones de Diseño Técnico

Multi-tenant desde el inicio es correcto — pero debe definirse la estrategia: schema-per-tenant vs row-level isolation antes de diseñar la DB. PostgreSQL con RLS (Row Level Security) es la opción más limpia para SaaS en GCP.
IA en el MVP — mencionada pero sin caso de uso concreto. Recomiendo no incluirla en Fase 1 para no comprometer velocidad del MVP. Dejarla como Fase 2.
El Design System existente no está documentado en el brief — riesgo de inconsistencia si los dos devs no lo conocen bien.


✅ Brief Simplificado — Fase 1 (Solo CRM)
VENTURA ENERGY — CRM COMERCIAL
Fase 1 · MVP · v1.1

OBJETIVO
─────────────────────────────────────────────
Digitalizar y dar trazabilidad al proceso comercial de Ventura Energy,
reemplazando el sistema actual en Notion con un CRM propio y escalable.

EQUIPO
─────────────────────────────────────────────
PO:           Héctor
Líder:        Karina Ibarra
Arquitecto:   Semi-Senior
Devs:         2 (en formación, con mentoring)

STACK CONFIRMADO
─────────────────────────────────────────────
Cloud:        GCP
OS:           Linux
Frontend:     React + Design System existente
DB:           PostgreSQL  ← RECOMENDADO, pendiente confirmación
Backend:      ← PENDIENTE (Node.js / Python / Go)

ENTIDADES CORE DEL CRM
─────────────────────────────────────────────
1. Empresa      → nombre, sector, tamaño, ciudad, intereses
2. Contacto     → nombre, teléfono, email, promotor, rol, empresa_id
3. Oportunidad  → estado pipeline, prioridad, valor estimado,
                  fecha esperada cierre, account_owner
4. Cotización   → versión, fecha emisión, vencimiento, monto,
                  corrida financiera*, modulación*
5. Interacción  → tipo (llamada/visita/nota), fecha, resultado,
                  fotos_gps*, recibo_cfe*
6. Visita Técnica → fecha, propósito, estado, agenda (opcional)

  * Campos en Notion — requieren confirmación si entran al MVP

PIPELINE (estados)
─────────────────────────────────────────────
Prospecto → Contactado → Cotización enviada → Negociación → Cerrado/Perdido

FUERA DEL MVP (Fase 1)
─────────────────────────────────────────────
✗ BOM               ✗ Contabilidad        ✗ Gestión de créditos
✗ Soporte técnico   ✗ Project Management  ✗ IA / scoring
✗ Multi-tenant      ✗ Módulos operacionales

CRITERIO DE DONE — FASE 1
─────────────────────────────────────────────
✓ CRUD completo de las 6 entidades
✓ Pipeline visual de oportunidades
✓ Historial de interacciones por empresa/contacto
✓ Generación y versionado de cotizaciones
✓ Agenda automática para visitas técnicas
✓ Autenticación y roles básicos (admin / comercial)

📋 Decisiones que deben tomarse ANTES de Sprint 0
#DecisiónResponsableUrgencia1Confirmar backend (Node / Python / Go)Arquitecto🔴 Crítica2Confirmar PostgreSQL como DBArquitecto + PO🔴 Crítica3¿Entran Corrida Financiera, Modulación, Recibo CFE al MVP?Héctor (PO)🔴 Crítica4Definir cronograma con hitos mínimosKarina + Héctor🟠 Alta5Documentar Design System para el equipo devArquitecto🟠 Alta6Estrategia de autenticación (JWT / OAuth / SSO)Arquitecto🟡 Media

Recomendación de arquitectura para esta fase
Dado que están en planificación, sugiero definir esto antes de escribir una línea de código:
[ React SPA ]
     ↕ REST / GraphQL
[ API Layer — Node.js o Python ]    ← decidir primero
     ↕
[ PostgreSQL en GCP Cloud SQL ]
     ↕
[ GCP Storage — archivos: fotos GPS, recibos CFE, contratos ]
La API debe ser stateless desde el día 1 para que la transición a multi-tenant (Fase 3) no requiera reescribir el core.

¿Quieres que profundice en el esquema de base de datos, el diseño de la API, o en la sesión de definición con el PO para cerrar los puntos abiertos?


El tiempo es salir en 6 meses con el CRM el BOM el RAI

POR LO QUE 
en dos meses tener el CRM listo, todo el mes enfocado en el crm y la planificacion del sistema 

Parte inicial es tener un documento de requisitos del sistema 
un diagrama entidad relacion 
un diagrama de user map 
y documentacion similar 
flask como api 
Backlog
Modulos definidos 


Actúa como un Senior Software Architect y Project Manager con mentalidad nórdica: pragmático, minimalista y directo. Tu objetivo es maximizar la eficiencia técnica y la claridad del negocio.

Directrices de Arquitectura:

Diseño Modular: Propón siempre soluciones desacopladas y escalables.

Seguridad por Diseño: Integra gestión de identidades y protección de datos desde la fase de esquema.

Estandarización: Prioriza el uso de JSON para intercambios de datos 


Directrices de Liderazgo:

Comunicación: Evita la palabrería. Sé breve y enfócate en la solución, no en el problema.

Documentación: Genera reportes técnicos formales y claros, similares a estándares académicos o de certificaciones profesionales.

Mentalidad de Producto: Alinea cada decisión técnica con la estrategia de marca (ej. layouts tipo Bento Grid o Apple Philosophy).

Restricciones:

No utilices jerga técnica innecesaria cuando se discutan temas de impacto humano o emocional.

Enfócate en lo que el sistema tiene y cómo optimizarlo, evitando redundancias. no utilices emojis y evita lineas divisoras


Brief de Preguntas — Sesión de Requisitos
Ventura Energy CRM ·





BLOQUE 1 — Negocio y Proceso Comercial

¿Cuál es el proceso comercial actual paso a paso, desde que llega un prospecto hasta que se cierra o se pierde?

¿Quién puede crear una cotización? 
¿Solo el área comercial o también el arquitecto/técnico?

¿Qué es una "Corrida Financiera"? 
¿Es un cálculo interno, un documento adjunto o ambos?

¿Qué es "Modulación"?
 ¿Es un producto, una configuración técnica del proyecto solar?

¿Un cliente puede tener múltiples oportunidades activas al mismo tiempo?

¿Qué significa que una cotización "venza"? 
¿Se archiva, se reactiva, se notifica al comercial?

¿Cuándo se genera una visita técnica? 
¿Quién la solicita y quién la atiende?


BLOQUE 2 — Usuarios y Roles

¿Quiénes van a usar el CRM? 
Lista los perfiles exactos (ej. director comercial, vendedor, técnico, administrador).
Director, Vendedor, Tecnico, Administrador
¿Qué puede ver y hacer cada perfil? 
El administrador puede modificar el sistema
el vendedor puede ver el estado de las ventas y clientes
el tecnico agendar visitas tecnicas 

¿Hay información que algunos no deben ver (ej. montos, datos de otros vendedores)?
¿Existe el concepto de "Account Owner"? 
Acount owner a cual director de la empresa le pertenece el contacto 
¿Un vendedor solo ve sus propios clientes o todos?

¿Quién es el "Promotor" que aparece en Notion? ¿Es un usuario interno o un contacto externo (canal, referido)?



BLOQUE 3 — Datos y Entidades

¿Una empresa puede tener múltiples contactos? 
Si
¿Hay un contacto principal?
Si
¿El "Recibo CFE" y las "Fotos GPS" son documentos adjuntos obligatorios o solo cuando aplica?
Es parte del proceso de cotizacion, pero puede darse muy pocos casos donde no exista (98% de los recibos se adjunten)
¿Qué información debe tener una cotización formal? 
¿Hay una plantilla actual en uso? Si

¿Las cotizaciones se generan en el sistema o se adjunta un PDF externo (Excel, Word)?
se debe de generar la cotizacion por el sistema
las cotizaciones tienen fecha de vencimiento
¿Qué es el campo "Contrato" en Notion? 
es el documento adjunto del contrato establecido y su versionado 
¿Es un documento adjunto post-cotización? 
¿Entra al MVP?
si
¿Cuáles son todos los estados posibles de una oportunidad (pipeline completo)?
sugiere algunos 

BLOQUE 4 — BOM y RAI (Para planificación de Fases 2 y 3)

¿Qué es el BOM en el contexto de Ventura Energy? ¿Es la lista de materiales de un proyecto solar específico?
¿El BOM está ligado a una cotización, a un proyecto o a ambos?
¿Qué es RAI? Define el módulo con una oración: "RAI permite a [usuario] hacer [acción] para lograr [resultado]."
¿BOM y RAI tienen dependencia con el CRM o son módulos independientes?


BLOQUE 5 — Integraciones y Operación

¿El sistema debe enviar notificaciones?
Si, basicas de inicio ¿Por qué canal (email, WhatsApp, interno)?
¿Se va a migrar la data actual de Notion al nuevo sistema? Si 
¿Cuántos registros existen hoy?
¿Existe algún sistema externo con el que el CRM deba conectarse (facturación, ERP, correo corporativo)?
De momento no es relevante
¿El sistema debe funcionar en móvil o solo en desktop?
Desktop y algunos dashboards en movil de ser posible pero no es prioridad 


BLOQUE 6 — Planificación y Entrega

¿Cuál es el criterio de aceptación del CRM?
 ¿Qué debe funcionar para considerar la Fase 1 completa?
¿Hay una fecha inamovible para el primer entregable?
¿Quién hace UAT (pruebas de aceptación)? ¿Será Héctor, el equipo comercial, o ambos? ambos
¿Los desarrolladores tienen disponibilidad completa o trabajan en paralelo con otros proyectos? disponibilidad completa de 5 horas lunes a viernes 
¿Existe un ambiente de staging separado de producción, o el primer deploy es directo?
Se deben de hacer ambos entornos 

Genera mas preguntas enfocandonos solo en el CRM



Lo que quedó sin responder de la Ronda 1
Antes de avanzar, estas respuestas de la ronda anterior siguen abiertas:
PreguntaEstado¿Qué es "Corrida Financiera"?Sin respuesta¿Qué es "Modulación"?Sin respuesta¿Quién es el "Promotor"?Sin respuesta¿Vendedor ve solo sus clientes o todos?Sin respuesta¿Hay información restringida por rol (montos, contactos)?Sin respuesta¿Fecha inamovible de entrega del CRM?Sin respuesta¿Cuántos registros existen hoy en Notion?Sin respuesta¿Cuándo se genera una visita técnica y quién la atiende?Sin respuesta

Pipeline — Propuesta para validación
Valida o corrige estos estados. Táchalo, agrega o reordena:
Nuevo prospecto
    ↓
Primer contacto realizado
    ↓
Recibo CFE recibido
    ↓
Corrida financiera generada
    ↓
Cotización enviada
    ↓
Visita técnica agendada  (opcional)
    ↓
Cotización aceptada
    ↓
Contrato firmado
    ↓
Cerrado ganado  /  Cerrado perdido  /  Congelado
¿Este flujo representa el proceso real? ¿Falta algún estado?

BLOQUE 7 — Cotización (profundidad)

¿Qué campos debe tener la cotización generada por el sistema? Describe la plantilla actual aunque sea a grandes rasgos (ej. datos del cliente, descripción del sistema solar, precio, condiciones).
¿Una cotización puede modificarse después de enviada o se crea una nueva versión?
¿Cuántas versiones de cotización puede tener una oportunidad? ¿Hay un límite?
¿Qué pasa cuando una cotización vence y el cliente no ha respondido? ¿Se notifica automáticamente, se cambia el estado o solo queda como registro?
¿La cotización la aprueba alguien internamente antes de enviarse al cliente?
¿El contrato siempre viene después de una cotización aceptada, o puede existir sin cotización?


BLOQUE 8 — Interacciones y Seguimiento

¿Qué tipos de interacción existen hoy? (ej. llamada, email, visita, WhatsApp, reunión). Lista todos los que el equipo usa.
Cuando se registra una llamada, ¿qué información se captura obligatoriamente? ¿Solo la fecha y nota, o también duración, resultado, próxima acción?
¿Existe un proceso de "revisión de clientes congelados"? ¿Cada cuánto tiempo se revisa y quién es responsable?
¿Qué razones de pérdida existen actualmente? ¿Son categorías fijas o texto libre?
¿Cómo se mide la satisfacción del cliente hoy? ¿Es una nota, un número, una encuesta?


BLOQUE 9 — Visita Técnica

¿Qué información debe contener la agenda generada automáticamente para una visita técnica?
¿Quién recibe la agenda, solo el técnico o también el cliente?
¿Las fotos GPS se toman durante la visita técnica específicamente, o pueden subirse en cualquier momento del proceso?
¿Una oportunidad puede tener múltiples visitas técnicas?
¿Qué estados tiene una visita técnica? (ej. agendada, completada, cancelada, reprogramada)


BLOQUE 10 — Roles y Permisos (profundidad)

El administrador "puede modificar el sistema" — ¿esto significa gestión de usuarios y configuración, o también puede editar registros comerciales de otros?
¿El director puede ver las oportunidades y clientes de todos los vendedores, o solo los que le están asignados como Account Owner?
¿El técnico solo agenda visitas o también puede ver la información del cliente y la cotización asociada?
¿Existe un rol de "solo lectura" o de gerencia que requiera ver reportes pero no crear registros?
¿Los vendedores pueden ver los montos de las cotizaciones de sus colegas?


BLOQUE 11 — Notificaciones

¿Qué eventos deben generar una notificación? Marca los que aplican o agrega:

Cotización próxima a vencer
Cotización vencida
Visita técnica agendada
Cliente sin contacto en X días
Nueva oportunidad asignada
Contrato subido


¿Las notificaciones son internas (dentro del sistema) o también por email?
¿Quién recibe cada notificación? ¿El vendedor asignado, el director, ambos?


BLOQUE 12 — Migración de Notion

¿La migración de Notion es un requisito para considerar el CRM como "listo", o puede usarse el nuevo sistema en paralelo durante un periodo?
¿Los registros de Notion tienen data completa o hay campos vacíos e inconsistentes que requieran limpieza previa?
¿Quién es responsable de validar que la data migrada es correcta, el equipo técnico o el equipo comercial?







-------------------------------
## Sesión de Requisitos — Ronda 2
### Solo CRM · Preguntas de profundidad

---

### Lo que quedó sin responder de la Ronda 1

Antes de avanzar, estas respuestas de la ronda anterior siguen abiertas:

| Pregunta | Estado |
|---|---|
| ¿Qué es "Corrida Financiera"? | es EL TIPO de pago, planes de financiamiento, si es a credito, si es efectivo etc |
| ¿Qué es "Modulación"? | es la Propuesta
Sistema
Fotovoltaico |
| ¿Quién es el "Promotor"? | es el vendedor |
| ¿Vendedor ve solo sus clientes o todos? | solo clientes asignados |
| ¿Hay información restringida por rol (montos, contactos)? | en el MVP no es mejor arquitecturarlo desde el dise;o o recomiendas definir despues? |
| ¿Fecha inamovible de entrega del CRM? | Junio 15 |
| ¿Cuántos registros existen hoy en Notion? | desconozco |
| ¿Cuándo se genera una visita técnica y quién la atiende? | Cuando comparten el recibo se agenda la visita y luego se hace la cotizacion, lo hace el tecnico debe de tener un estandar de revision |

---

### Pipeline — Propuesta para validación

Valida o corrige estos estados. Táchalo, agrega o reordena:

```
Nuevo prospecto
    ↓
Primer contacto realizado
    ↓
Recibo CFE recibido / O documento de requisitos recivido
    ↓
    Visita tecnica agendada 
    ↓
Cotización enviada
    ↓
    Ajuste de cotizacion hasta aceptar 
    ↓
Cotización aceptada
    ↓
Contrato firmado
    ↓
Cerrado ganado  /  Cerrado perdido  /  Congelado / Perdido * Los tiempos pueden llevar hasta meses segun el cliente 

Corrida financiera adjuntada



### BLOQUE 7 — Cotización (profundidad)

31. ¿Qué campos debe tener la cotización generada por el sistema? Describe la plantilla actual aunque sea a grandes rasgos (ej. datos del cliente, descripción del sistema solar, precio, condiciones).
Datos de la empresa, datos del cliente, descripcion, unidades precio, condicion, metodo de pago, cierra 

32. ¿Una cotización puede modificarse después de enviada o se crea una nueva versión?
se crea una nueva version para tener el control. las cotizaciones no se guardan en el sistema para ahorrar db pero si se generar al momento y se descargan

33. ¿Cuántas versiones de cotización puede tener una oportunidad? 

¿Hay un límite? no 

34. ¿Qué pasa cuando una cotización vence y el cliente no ha respondido? solo se marca como vencida

35. ¿La cotización la aprueba alguien internamente antes de enviarse al cliente? por definir 

36. ¿El contrato siempre viene después de una cotización aceptada, o puede existir sin cotización? no puede existir sin cotizacion adjunta

---

### BLOQUE 8 — Interacciones y Seguimiento

37. ¿Qué tipos de interacción existen hoy?llamada, email, visita, WhatsApp, reunin 

38. Cuando se registra una llamada, ¿qué información se captura obligatoriamente?
 Fecha Cliente duracion y nota 

39. ¿Existe un proceso de "revisión de clientes congelados"? ¿Cada cuánto tiempo se revisa y quién es responsable?
Si, por definir pero supongamos la naturaleza de sistemas de energias renovalbes puede ser 3 meses incluso ... pero no tengo seguro el mercado

40. ¿Qué razones de pérdida existen actualmente? ¿Son categorías fijas o texto libre?
Dejala como pregunta por definir

41. ¿Cómo se mide la satisfacción del cliente hoy? ¿Es una nota, un número, una encuesta?
Por definir


### BLOQUE 9 — Visita Técnica

42. ¿Qué información debe contener la agenda generada automáticamente para una visita técnica?
lo basico

43. ¿Quién recibe la agenda, solo el técnico o también el cliente?
ambos (maybe en conjunto con google calendar)

44. ¿Las fotos GPS se toman durante la visita técnica específicamente, o pueden subirse en cualquier momento del proceso?
en cualquier momento

45. ¿Una oportunidad puede tener múltiples visitas técnicas?
si

46. ¿Qué estados tiene una visita técnica?  agendada, completada, cancelada, reprogramada



### BLOQUE 10 — Roles y Permisos (profundidad)

47. El administrador "puede modificar el sistema" — ¿esto significa gestión de usuarios y configuración, o también puede editar registros comerciales de otros?
ambos pero no lo veo relevante en el mvp

48. ¿El director puede ver las oportunidades y clientes de todos los vendedores, o solo los que le están asignados como Account Owner?
si

49. ¿El técnico solo agenda visitas o también puede ver la información del cliente y la cotización asociada?


50. ¿Existe un rol de "solo lectura" o de gerencia que requiera ver reportes pero no crear registros?
por definir 

51. ¿Los vendedores pueden ver los montos de las cotizaciones de sus colegas?



### BLOQUE 11 — Notificaciones

52. ¿Qué eventos deben generar una notificación? 
    - Cotización próxima a vencer   
    - Cotización vencida
    - Visita técnica agendada

53. ¿Las notificaciones son internas (dentro del sistema) o también por email?
internas

54. ¿Quién recibe cada notificación? ¿El vendedor asignado, el director, ambos?

el asignado 

### BLOQUE 12 — Migración de Notion

55. ¿La migración de Notion es un requisito para considerar el CRM como "listo", o puede usarse el nuevo sistema en paralelo durante un periodo?
no, de momento no 

56. ¿Los registros de Notion tienen data completa o hay campos vacíos e inconsistentes que requieran limpieza previa? requieren limpieza

57. ¿Quién es responsable de validar que la data migrada es correcta, el equipo técnico o el equipo comercial? equipo tecnico

Nota* nos agrada como organiza la informacion hubspot - Empresa, Clientes, Visitas etc etc
