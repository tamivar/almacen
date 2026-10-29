# Almacén Digital COONAPROSAL V8.1

Mantiene todas las funciones de V8 y mejora específicamente la relocalización.

## Relocalización visual por tarima
- La fila ya no se presenta como si se moviera completa.
- Cada tarjeta representa UNA sola tarima.
- Se muestran únicamente tarimas que pueden moverse directamente.
- Puede:
  1. arrastrar una o varias tarjetas al recuadro de destino;
  2. seleccionar una o varias tarimas mediante lista.
- Las tarimas no seleccionadas permanecen donde están.
- El ID interno ya no se muestra al usuario.
- La tarjeta visible muestra:
  - posición y nivel,
  - SKU,
  - lote,
  - fecha.
- Antes de guardar se muestra una vista previa.
- El movimiento se confirma antes de actualizar el inventario.
- Inventario e historial se actualizan automáticamente al confirmar.

## Entrada automática
Se mantiene:
- completar N1 y N2 de una fila;
- luego pasar a la siguiente fila;
- N3 únicamente con autorización de sobrealmacenamiento.

## Ejecutar
pip install -r requirements.txt
streamlit run app.py
