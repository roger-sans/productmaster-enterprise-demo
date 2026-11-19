# Caso de estudio: de la reclasificación a ProductMaster

## Problema de negocio

En una organización ficticia que comercializa herramientas y productos para pintura, **las mismas referencias se interpretan de manera distinta según el departamento**. Producto necesita descripciones técnicas, Comercial exige un catálogo navegable, Compras maneja denominaciones de proveedores, Operaciones utiliza referencias de sistemas de origen y Finanzas necesita dimensiones coherentes para analizar resultados.

El objetivo de ProductMaster es acordar un vocabulario común, establecer responsables funcionales y mantener una representación confiable de cada producto sin sustituir indiscriminadamente los sistemas operacionales.

## Responsabilidad del Product Owner

El trabajo no consiste únicamente en desarrollar un catálogo. El Product Owner transforma conflictos entre departamentos en decisiones verificables: requisitos de clasificación, reglas de completitud, propietarios de datos, condiciones de aprobación, backlog priorizado y contratos consumibles por otros sistemas.

En este caso recreado, las fases son:

1. **Descubrimiento y coordinación.** Identificar por qué una referencia se agrupa de forma distinta en Producto, Comercial y Compras. Separar descripciones de origen, etiquetas comerciales y clasificación corporativa.
2. **Consenso semántico.** Definir niveles `Family → Subfamily → Type`, códigos estables y excepciones legítimas cuando una subfamilia es terminal.
3. **Atributos técnicos.** Definir tipos, unidades, valores permitidos y aplicabilidad por categoría. Una medida como ancho de trabajo no equivale a un formato comercial ni a una categoría.
4. **Gobierno.** Documentar quién propone, quién revisa y quién aprueba una reclasificación. No aplicar cambios a escondidas, ni permitir la autoaprobación.
5. **Producto reutilizable.** Exponer la información de manera trazable por API y vista de consulta, con identificadores, procedencia y versión.
6. **ProductIntelligence.** Vincular el contexto gobernado con métricas temporales de ventas, existencias y pedidos para ofrecer análisis explicables, sin introducir esos hechos dentro de los atributos maestros.

## Qué puede comprobar un evaluador

La aplicación permite explorar **640 referencias ficticias**, una jerarquía de **13 familias, 59 subfamilias y 120 tipos**, **25 definiciones de atributos**, fichas de producto, solicitudes de modificación, aprobaciones y métricas analíticas sintéticas. El código Python, la API, la documentación de decisiones y las pruebas están incluidos en el repositorio.

Los números, aprobaciones y situaciones de negocio de este repositorio son **simulados**. No representan métricas ni resultados de una empresa real.

## Por qué es relevante para un perfil de Product Owner de Datos

Demuestra capacidad para estructurar un producto de datos en torno a objetivos de negocio, gestionar dependencias y conflictos funcionales, traducir reglas en criterios de aceptación y conservar suficiente profundidad técnica para discutir arquitectura, calidad, gobierno y contratos de datos con ingeniería.

Consulta [la coordinación transversal](02-cross-functional-delivery.md), [el inventario funcional](03-taxonomy-and-attributes.md) y [el recorrido demostrable](08-demo-walkthrough.md).
