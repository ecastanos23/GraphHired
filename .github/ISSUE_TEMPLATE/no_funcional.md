---
name: "HU NF: Requisito No Funcional"
about: Template para arquitectura, seguridad y rendimiento
title: "HU NF XX: [Nombre del Atributo de Calidad]"
labels: ["HU NF", "Must Have"]
assignees: ''

---

<!--
COMENTARIO DE ARCHIVO - GRAPHHIRED
Plantilla de issue no funcional. Partes: atributo de calidad, descripcion, criterios medibles y contexto tecnico.
-->

### 1. Descripción Técnica
**Atributo de Calidad:** [Ej: Seguridad, Escalabilidad, Disponibilidad]
**Descripción:** Detallar el requisito técnico (ej: "El sistema debe procesar el PDF del CV en menos de 5 segundos").

### 2. Justificación Técnica
*¿Por qué es necesario para GraphHired?*
(Ej: "Garantizar que el Agente de Perfil no bloquee el hilo principal del backend").

### 3. Condiciones de Aceptación (CA)
- [ ] **CA1:** El sistema debe cumplir con el estándar [Ej: OWASP / Cifrado AES-256].
- [ ] **CA2:** [Ej: El rate limiting debe dispararse tras 5 peticiones fallidas].
- [ ] **CA3:** [Ej: La arquitectura debe seguir el patrón de capas definido].

### 4. Tareas de Implementación
- [ ] [Tarea 1: Configurar Middleware de seguridad]
- [ ] [Tarea 2: Implementar logs de auditoría]
- [ ] [Tarea 3: Realizar pruebas de carga]

### 5. Prioridad (MoSCoW)
- [ ] Must Have
- [ ] Should Have
- [ ] Could Have
