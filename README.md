# Almacén Digital COONAPROSAL

Aplicación Streamlit para controlar el inventario de tarimas del almacén:
ubicación por zona, fila, posición y nivel; entradas, salidas, reacomodos,
criterio PEPS e historial de movimientos.

Todo el código está en `app.py`. Los datos se guardan en CSV dentro de `data/`.

## Ejecutar

```
pip install -r requirements.txt
streamlit run app.py
```

En Windows también se puede usar `INICIAR_ALMACEN.bat`.

## Archivos

| Archivo | Contenido |
|---|---|
| `app.py` | Toda la aplicación (reglas + interfaz). |
| `data/warehouse_state_v7.csv` | Inventario: una fila por **espacio** (zona, posición, nivel) y su estado. |
| `data/movements_v7.csv` | Historial: una fila por movimiento de tarima. |
| `data/product_catalog_v7.csv` | Catálogo SKU → producto. |
| `generar_claves.py` | Genera los hash bcrypt de las contraseñas. |
| `.streamlit/secrets.toml` | Contraseñas y clave de cookie (no se sube a git). |

## Modelo del almacén

- **Zonas** (`ZONES`): cada zona tiene un número de filas, una capacidad en
  posiciones y un prefijo (`W` = Walmart, `G` = Almacenamiento general, etc.).
  La suma de posiciones debe dar `DECLARED_CAPACITY` (847).
- **Fila** (`F01`, `F02`…): se accede por un solo extremo. `depth = 1` es la
  posición más cercana al acceso; el número mayor es el fondo.
- **Posición** (`W001`…): lugar físico en el piso.
- **Nivel** (N1, N2, N3): N1 es el piso. N2 y N3 son remontado sobre la tarima
  de abajo.

Cada espacio (posición + nivel) es una fila del CSV de inventario con
`status` = `Disponible` u `Ocupada`.

## Reglas de negocio

1. **Una fila = un solo SKU.** Una fila vacía acepta cualquier SKU; una fila
   ocupada solo acepta el mismo SKU (`row_accepts_sku`).
2. **Remontado.** Solo se coloca en N2/N3 si los niveles de abajo están
   ocupados, y solo se retira la tarima de más arriba (`can_place_on_level`,
   `can_remove`).
3. **Orden de llenado.** N1 de la fila, luego N2, luego la siguiente fila.
   N3 es sobrealmacenamiento y solo se usa si el usuario lo autoriza.
4. **Zonas sin remontado.** Las zonas en `SINGLE_LEVEL_ZONES` (hoy solo
   **Walmart**) solo admiten N1. La regla está en `max_level_for_zone` y
   `can_place_on_level`, y la interfaz desactiva N2/N3 para esas zonas. Si al
   cargar hay tarimas en niveles no permitidos, se muestra un aviso (no se
   borran).
5. **PEPS.** El producto nuevo va al fondo de la fila; sale primero el lote
   con fecha de producción más antigua que esté accesible (sin tarimas delante
   ni encima).
6. **Tarimas mixtas** (bultos de varios lotes en una tarima):
   - `lot` = `"22-10 + 21-10"` (para búsquedas y vistas),
   - `production_date` = fecha **más antigua** (la que cuenta para PEPS),
   - `bundles` = total de bultos,
   - `lot_detail` = desglose `lote|fecha|bultos;lote|fecha|bultos`
     (vacío si la tarima es de un solo lote).

   Una tarima mixta se mueve y sale completa. Funciones de ayuda:
   `pallet_lot_parts`, `summarize_lot_parts`, `lot_detail_label`.

## Pantallas (en orden en `app.py`)

| Sección | Qué hace |
|---|---|
| Inicio de sesión | Contraseña → rol `editor` o `visualizador`. |
| Panel general | Indicadores: inventario por SKU, rotación, consulta de producto, ocupación por zona. |
| Mapa | Vista de cada fila con sus niveles; búsqueda por SKU, lote o producto y resaltado del lote más antiguo. |
| **Entrada** | Modo **PEPS automático** (la app propone ubicaciones) o **Manual** (el usuario marca las posiciones; viene pre-marcada la sugerencia). Admite varias tarimas por operación y tarimas mixtas. Siempre muestra una propuesta que se confirma antes de guardar. |
| **Salida** | Despacho de una o varias tarimas, automático PEPS o manual, indicando los bloqueos que hay que liberar. |
| **Relocalizar** | Mover tarimas accesibles de una fila a otra compatible (arrastrando o por lista). |
| **Reacomodo PEPS** | Revisa si el orden de lotes de una fila cumple PEPS y propone el orden correcto (no mueve nada; los movimientos se hacen en Relocalizar). |
| Consulta global | Búsqueda en toda la bodega, con tarimas delante/encima y desglose de mixtas. |
| Historial | Movimientos, filtros, descarga en Excel y corrección de un registro (borrar línea o anular una entrada). |
| Catálogo | Edición SKU → producto. |
| Administración | Borrar historial o reiniciar el almacén. |

Todo cambio pasa por `occupy_slot` / `clear_slot` (inventario) y `log_move`
(historial), y se guarda con `save_state` / `save_moves`. Esas funciones
exigen el rol editor (`require_editor`).

## Dónde cambiar cosas comunes

| Quiero… | Cambiar |
|---|---|
| Agregar o cambiar una zona | `ZONES` (y `DECLARED_CAPACITY` si cambia el total). |
| Que otra zona no se remonte | Agregarla a `SINGLE_LEVEL_ZONES`. |
| Agregar un turno | `TURNOS`. |
| Cambiar el orden de llenado | `next_slot_in_row`, `plan_batch_entry_across_rows`. |
| Agregar una columna al inventario | `STATE_COLUMNS` y los `defaults` de `load_state` (los CSV viejos se completan solos). |

## Acceso y roles

Las cuentas se leen de `st.secrets` y las contraseñas se validan con bcrypt.
También se requiere una clave aleatoria de al menos 32 bytes para firmar la
cookie de sesión (8 horas). Genérela con
`python -c "import secrets; print(secrets.token_hex(32))"` y los hash con
`python generar_claves.py`. Estructura de `.streamlit/secrets.toml`:

```toml
cookie_key = "<CLAVE_ALEATORIA_GENERADA>"

[usuarios.editor]
rol = "editor"
password_hash = "<HASH_BCRYPT_DEL_EDITOR>"

[usuarios.visualizador]
rol = "visualizador"
password_hash = "<HASH_BCRYPT_DEL_VISUALIZADOR>"
```

En Streamlit Community Cloud, copie esta estructura en
**App settings → Secrets** con los valores reales. No publique contraseñas
ni el archivo local de secretos.

`visualizador` = solo lectura. `editor` = puede operar y guardar.

**Sesión recordada (cookie).** Al iniciar sesión se guarda una cookie
firmada con `cookie_key` que mantiene la sesión 8 horas, aunque se recargue
la página. Reglas:

- Si el usuario escribe una contraseña, manda el resultado de esa contraseña;
  la cookie nunca la reemplaza.
- "Cerrar sesión" invalida y borra la cookie, y esa pestaña vuelve a pedir
  contraseña.
- Para cerrar **todas** las sesiones abiertas, cambie `cookie_key` (en el
  archivo local y en los Secrets de Cloud).

## Persistencia en Streamlit Community Cloud

Los datos se guardan en los CSV de `data/`. En Streamlit Community Cloud el
disco no es persistente: los cambios pueden perderse al reiniciar o volver a
desplegar la app. Para conservarlos de forma duradera en Cloud hace falta un
almacenamiento externo.
