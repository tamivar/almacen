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

## Acceso y roles

La aplicación obtiene las cuentas desde `st.secrets` y valida las contraseñas
con bcrypt. La estructura esperada para `.streamlit/secrets.toml` es:

```toml
[users.editor]
rol = "editor"
password_hash = "<HASH_BCRYPT_DEL_EDITOR>"

[users.visualizador]
rol = "visualizador"
password_hash = "<HASH_BCRYPT_DEL_VISUALIZADOR>"
```

En Streamlit Community Cloud, copie manualmente esta misma estructura en
**App settings → Secrets**, sustituyendo los marcadores por los valores
privados correspondientes. No incluya contraseñas en texto plano ni publique
el archivo local de secretos.

El rol `visualizador` tiene acceso de solo lectura. El rol `editor` puede
realizar operaciones y guardar cambios.

## Persistencia en Streamlit Community Cloud

El inventario, el historial y el catálogo continúan guardándose en los CSV
existentes dentro de `data/`. El sistema de archivos local de Streamlit
Community Cloud no ofrece persistencia garantizada entre reinicios o
reimplementaciones; para conservar cambios de forma duradera en Cloud se
requiere almacenamiento externo persistente. Esta aplicación no cambia el
formato ni la ubicación actual de esos datos.
