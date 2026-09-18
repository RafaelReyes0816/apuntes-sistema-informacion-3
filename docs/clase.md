Clear Architecture:

La arquitectura limpia es un concepto de diseño de software, nos ayuda a hacer aplicaciones más sostenibles, escalables mejorando la mantenibilidad y adaptabilidad.

Características:
Tiene el principio de SOLID, facilita la creación del software sea legible y mantenible. Está orientado a interfaces

Principio clave
Separación de preocupaciones en capas

Capas:
-Entidades: Nucleo del negocio, independientes de otras capas
-Casos de uso: lógica de la aplicación, coordinación de entidades
-Adaptadores: Interfaz con UI, base de datos y servicios externos
-Frameworks y herramientas: bibliotecas y frameworks externos.
Visual sugerido: Ilustración de clean architecture de Robert Marin. 

Principios y patrones claves:
-DIP
-loC
-DI
-SoC
-Repository Pattern

Gestion de dependencias:
Promueve la minimización de las dependencias de componentes.

Comparación con otras arquitecturas:
-Arqutiectura monolítica: Agrupa todas las funcionalidades en un solo bloque
-Arquitectura en capas: Está enfocada a la organización del software en capas jerárquicas.
-Microservicios: Divide las aplicaciones en servicios pequeños e independientes. Esto permite despliegues y escalado de componentes de manera aislada, facilitando resiliencia y agilidad en el desarrollo.

Variantes:
-Arquitectura Hexagonal
-Arquitectura Cebolla
-DDD, CQRS, Microservicios

Consideraciones importantes:
-Comprensión clara del dominio del problema
-Division clara de responsabilidades
-Pruebas unitarias

Como empezar:
-Comprender principios
-Analizar y modelar

Beneficios:
-Codigo mantenible
-Mayor escalabilidad
-Facil adaptación
