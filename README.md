# Proyecto Final — Sistema de Gestión de Laboratorio Clínico

## Introducción
El proyecto consiste en un sistema web para la gestión de un laboratorio clínico, desarrollado con Python y Django. Su objetivo es digitalizar y automatizar procesos médicos como el registro de pacientes, citas, resultados y generación de documentos PDF.

## Objetivo del Sistema
Centralizar la información clínica en una base de datos segura y organizada, eliminando el uso de registros físicos y facilitando el acceso según el rol de cada usuario.

## Tecnologías Utilizadas
- Python 3.11
- Django 4.2
- Microsoft SQL Server 2019
- HTML, CSS y Bootstrap
- ReportLab
- qrcode
- Git y GitHub

## Roles del Sistema
- Administrador
- Médico
- Técnico de laboratorio
- Recepcionista
- Paciente

## Funcionalidades Principales
### Autenticación
Permite iniciar sesión mediante usuario o correo electrónico y redirige automáticamente según el rol.

### Gestión de Pacientes
Registro, actualización y consulta de información clínica de pacientes.

### Gestión de Citas
Asignación de citas médicas con prioridad normal o urgente.

### Resultados Médicos
Ingreso de resultados clínicos con rangos de referencia automáticos.

### Generación de PDF
Creación de expedientes médicos en PDF con código QR de verificación.

## Base de Datos
Se utilizó SQL Server para garantizar:
- Integridad de datos
- Soporte multiusuario
- Escalabilidad
- Mayor seguridad

## Pruebas Realizadas
- Validación de inicio de sesión
- Control de errores
- Verificación de roles
- Pruebas de formularios y validaciones
- Corrección de errores en rutas y templates

## Conclusión
El sistema logró automatizar procesos importantes dentro de un laboratorio clínico mediante una solución moderna, organizada y segura. Además, permitió aplicar conocimientos de ingeniería de software, bases de datos y desarrollo web.

## Trabajo Futuro
- Implementar API REST
- Agregar autenticación en dos pasos
- Incorporar estadísticas y reportes
- Desarrollar versión móvil
- Migrar frontend a React o Vue
