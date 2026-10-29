
from __future__ import annotations

from pathlib import Path
from datetime import date, datetime
from io import BytesIO
import html
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from streamlit_sortables import sort_items

LOGO_PATH = Path(__file__).resolve().parent / "img" / "salsol.png"

# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Almacén Digital - COONAPROSAL",
    page_icon=str(LOGO_PATH),
    layout="wide",
)


DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

STATE_FILE = DATA_DIR / "warehouse_state_v7.csv"
MOVES_FILE = DATA_DIR / "movements_v7.csv"
CATALOG_FILE = DATA_DIR / "product_catalog_v7.csv"
DECLARED_CAPACITY = 847

TURNOS = ["Turno 1", "Turno 2"]
MAX_LEVELS = 3

# Cada fila se modela desde el lado de acceso hacia el fondo.
# depth = 1 es la posición más cercana al acceso.
ZONES = {
    "Almacenamiento 0002-0007-00503": {
        "rows": 10,
        "capacity_positions": 200,
        "prefix": "A",
        "access_side": "izquierda",
    },
    "Almacenamiento general": {
        "rows": 15,
        "capacity_positions": 300,
        "prefix": "G",
        "access_side": "izquierda",
    },
    "Zona industrial": {
        "rows": 20,
        "capacity_positions": 160,
        "prefix": "I",
        "access_side": "izquierda",
    },
    "Walmart": {
        "rows": 6,
        "capacity_positions": 54,
        "prefix": "W",
        "access_side": "izquierda",
    },
    "Sales especiales": {
        "rows": 5,
        "capacity_positions": 60,
        "prefix": "S",
        "access_side": "izquierda",
    },
    "Material de empaque": {
        "rows": 14,
        "capacity_positions": 42,
        "prefix": "E",
        "access_side": "izquierda",
    },
    "Producción diaria": {
        "rows": 3,
        "capacity_positions": 25,
        "prefix": "P",
        "access_side": "izquierda",
    },
    "Devoluciones / Cuarentena": {
        "rows": 2,
        "capacity_positions": 6,
        "prefix": "D",
        "access_side": "izquierda",
    },
}


LOT_COLORS = [
    "#FDE68A",
    "#86EFAC",
    "#67E8F9",
    "#93C5FD",
    "#C4B5FD",
    "#F0ABFC",
    "#FDA4AF",
    "#FDBA74",
]

STATE_COLUMNS = [
    "zone",
    "row_id",
    "depth",
    "position",
    "level",
    "sku",
    "product",
    "lot",
    "production_date",
    "entry_shift",
    "bundles",
    "status",
    "last_update",
]

MOVE_COLUMNS = [
    "timestamp",
    "shift",
    "movement_type",
    "origin",
    "destination",
    "zone_origin",
    "zone_destination",
    "row_origin",
    "row_destination",
    "sku",
    "product",
    "lot",
    "production_date",
    "bundles",
    "notes",
]



# ============================================================
# CATÁLOGO DE PRODUCTOS
# ============================================================

CATALOG_COLUMNS = [
    "sku",
    "product",
    "category",
    "unit",
    "suggested_zone",
]

DEFAULT_CATALOG = [{'sku': '0007', 'product': 'Sal Solar 500g C/F 1x25 unid', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Almacenamiento 0002-0007-00503'}, {'sku': '0002', 'product': 'Sal Sol 500g C/F1x25 unid', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Almacenamiento 0002-0007-00503'}, {'sku': '0005', 'product': 'Sal Sol 500g S/F 1x50 unid', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '0010', 'product': 'Sal Sol Dorada Salero100g', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '0014', 'product': 'Sal Sol Parrillera frasco 550g', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00503', 'product': 'Sal El Hada 500g 1x25 unid', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Almacenamiento 0002-0007-00503'}, {'sku': '00517', 'product': 'Sal Sol Marina bolsa 550g 1x25uds', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00520', 'product': 'Sal Sol Marina frasco 550g', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00521', 'product': 'Sal Sol Dorada frasco 550g', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00522', 'product': 'Sal Sol LIGHT 230g', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00523', 'product': 'Sal Sol Himalaya 230g (fina)', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00524', 'product': 'Sal Sol Himalaya 230g (gruesa)', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00526', 'product': 'Sal Sol KOSHER 1kg', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00527', 'product': 'Sal Sol Parrillera 1kg', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00528', 'product': 'Sal Sol Marina 1kg', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00529', 'product': 'Sal Sol Especias (jardin) 1kg', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00530', 'product': 'Sal Sol Himalaya (fina) 1kg', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00535', 'product': 'Sal Sol Himalaya (fina) 400g', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '0074', 'product': 'Sal Solar 500g S/F 1x50 unid', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '0149', 'product': 'Sal Sol Parrillera bolsa 550g 1x25uds', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': 'S0002', 'product': 'Sal Sol 500g C/F 1x25 unid', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00511', 'product': 'Hierbas del Jardín 400g', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00512', 'product': 'Hierbas Aromáticas 400g', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00513', 'product': 'Hierbas Provenzales 400g', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00536', 'product': 'Sal Himalaya Fina Salerito 100 gr', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00504', 'product': 'Molino Sal Sol Marina 120g', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00506', 'product': 'Molino Sal Sol Himalaya 120g', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '0007-2', 'product': 'Sal Solar C/F 500grs spack(10*2)', 'category': 'Retail', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '9046', 'product': 'Sal Solar 90% 46 kg', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Almacenamiento general'}, {'sku': 'D9046', 'product': 'Sal Solar 90% (DOS PINOS) 46 kg', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '9525', 'product': 'Sal Solar 95% 25 kg', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00516', 'product': 'Sal Solar Fina para queso 25 kg', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Zona industrial'}, {'sku': '9025', 'product': 'Sal Solar 90% 25 kg', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Almacenamiento general'}, {'sku': '9246', 'product': 'Sal Sol Roca 46 kg', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00514', 'product': 'Sal Sol Alta Pureza sin yodo 25 kg_pe', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '0021', 'product': 'Sal Solar Nacional 25 kg', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Zona industrial'}, {'sku': '0018', 'product': 'Sal Sol Alta Pureza 25 kg_ch', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': 'A9546', 'product': 'Sal Solar 95% con aditivo 46 kg', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '9546', 'product': 'Sal Solar 95% 46 kg', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Almacenamiento general'}, {'sku': '9225', 'product': 'Sal Sol Roca 25 kg', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Almacenamiento general'}, {'sku': '00510', 'product': 'Sal Cocinada 46kg', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': 'D951000', 'product': 'Sal Solar Dos Pinos 95% 1 TM', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00518', 'product': 'Sal Solar con Yodo y Fluor 25 kg', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': 'D9546', 'product': 'Sal Solar 95% (DOS PINOS) 46 kg', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '0144', 'product': 'Sal Sol Parrillera 25 kg', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '0789', 'product': 'Sal Sol Parrillera con Yodo y Fluor 25 kg', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00191', 'product': 'Sal Sol para Piscinas 25kg', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00192', 'product': 'Sal Sol tipo talco 25kg', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '0034', 'product': 'Sal Sol Mina 25 kg', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00507', 'product': 'Sal Sol Cloradores 25kg (pellets de sal)', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00531', 'product': 'Sal Sol Gruesa Media 25kg', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00532', 'product': 'Sal Sol Himalaya Fina 25kg', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00533', 'product': 'Sal Sol Himalaya Gruesa 25kg', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00534', 'product': 'Sal Sol Alta Pureza 25kg_tk', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Zona industrial'}, {'sku': '0139', 'product': 'Sal Sol Industrial Light 25 kg', 'category': 'Industrial', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00537', 'product': 'Doypack Sal Sol Parrillera 400g 1x12uds', 'category': 'Portafolio adicional', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00538', 'product': 'Doypack Sal Sol Marina 400g 1x12uds', 'category': 'Portafolio adicional', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00539', 'product': 'Doypack Sal Sol Himalaya Fina 400g 1x12uds', 'category': 'Portafolio adicional', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00540', 'product': 'Doypack Sal Sol Himalaya Gruesa 400g 1x12uds', 'category': 'Portafolio adicional', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '02027', 'product': 'Sal de Aqui bulto de 25 unidades 500grs', 'category': 'Portafolio adicional', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00534-1', 'product': 'Sal Sol Alta Pureza 25kg_TK', 'category': 'Portafolio adicional', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}, {'sku': '00497', 'product': 'AQUA Sun SMALL 18 kg', 'category': 'Portafolio adicional', 'unit': 'Bultos', 'suggested_zone': 'Sin asignación fija'}]


def save_catalog(catalog: pd.DataFrame) -> None:
    catalog = catalog.copy()

    for col in CATALOG_COLUMNS:
        if col not in catalog.columns:
            catalog[col] = ""

    catalog["sku"] = (
        catalog["sku"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    catalog["product"] = (
        catalog["product"]
        .astype(str)
        .str.strip()
    )

    catalog = catalog[
        catalog["sku"] != ""
    ].drop_duplicates(
        subset=["sku"],
        keep="last",
    )

    catalog[CATALOG_COLUMNS].to_csv(
        CATALOG_FILE,
        index=False,
        encoding="utf-8-sig",
    )


def load_catalog() -> pd.DataFrame:
    if not CATALOG_FILE.exists():
        save_catalog(
            pd.DataFrame(
                DEFAULT_CATALOG,
                columns=CATALOG_COLUMNS,
            )
        )

    catalog = pd.read_csv(
        CATALOG_FILE,
        dtype=str,
    ).fillna("")

    for col in CATALOG_COLUMNS:
        if col not in catalog.columns:
            catalog[col] = ""

    catalog["sku"] = (
        catalog["sku"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return catalog[CATALOG_COLUMNS]


def lookup_product(catalog: pd.DataFrame, sku: str):
    sku_clean = str(sku).strip().upper()

    if not sku_clean:
        return None

    match = catalog[
        catalog["sku"] == sku_clean
    ]

    if match.empty:
        return None

    return match.iloc[0].to_dict()


def upsert_product(
    catalog: pd.DataFrame,
    sku: str,
    product: str,
    category: str = "",
    unit: str = "Bultos",
    suggested_zone: str = "Sin asignación fija",
) -> pd.DataFrame:
    sku_clean = str(sku).strip().upper()
    product_clean = str(product).strip()

    if not sku_clean or not product_clean:
        return catalog

    catalog = catalog.copy()
    mask = catalog["sku"] == sku_clean

    if mask.any():
        idx = catalog[mask].index[0]
        catalog.at[idx, "product"] = product_clean

        if category:
            catalog.at[idx, "category"] = category

        if unit:
            catalog.at[idx, "unit"] = unit

        if suggested_zone:
            catalog.at[idx, "suggested_zone"] = suggested_zone

    else:
        catalog = pd.concat(
            [
                catalog,
                pd.DataFrame(
                    [
                        {
                            "sku": sku_clean,
                            "product": product_clean,
                            "category": category,
                            "unit": unit,
                            "suggested_zone": suggested_zone,
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )

    save_catalog(catalog)
    return load_catalog()


# ============================================================
# INDICADORES DE INVENTARIO
# ============================================================

def current_inventory_summary(
    state_df: pd.DataFrame,
    catalog: pd.DataFrame,
) -> pd.DataFrame:
    occupied = state_df[
        state_df["status"] == "Ocupada"
    ].copy()

    if occupied.empty:
        return pd.DataFrame(
            columns=[
                "sku",
                "product",
                "tarimas",
                "bultos",
                "lotes",
                "posiciones",
                "participacion_tarimas_pct",
            ]
        )

    summary = (
        occupied.groupby(
            "sku",
            dropna=False,
        )
        .agg(
            product_state=("product", "first"),
            tarimas=("level", "count"),
            bultos=("bundles", "sum"),
            lotes=("lot", lambda x: x[x.astype(str) != ""].nunique()),
            posiciones=("position", "nunique"),
        )
        .reset_index()
    )

    product_map = (
        catalog.set_index("sku")["product"]
        .to_dict()
        if not catalog.empty
        else {}
    )

    summary["product"] = summary.apply(
        lambda r: (
            product_map.get(str(r["sku"]).strip().upper())
            or r["product_state"]
            or "Sin nombre"
        ),
        axis=1,
    )

    total_pallets = int(summary["tarimas"].sum())

    summary["participacion_tarimas_pct"] = (
        summary["tarimas"] / total_pallets * 100
        if total_pallets > 0
        else 0
    )

    return summary[
        [
            "sku",
            "product",
            "tarimas",
            "bultos",
            "lotes",
            "posiciones",
            "participacion_tarimas_pct",
        ]
    ].sort_values(
        "tarimas",
        ascending=False,
    )


def operational_rotation_table(
    state_df: pd.DataFrame,
    moves_df: pd.DataFrame,
    catalog: pd.DataFrame,
) -> pd.DataFrame:
    inventory = current_inventory_summary(
        state_df,
        catalog,
    )

    if moves_df.empty:
        exits = pd.DataFrame(
            columns=[
                "sku",
                "salidas_tarimas",
            ]
        )
    else:
        move_work = moves_df.copy()

        exits = (
            move_work[
                move_work["movement_type"]
                .astype(str)
                .str.contains(
                    "Salida",
                    case=False,
                    na=False,
                )
            ]
            .groupby("sku")
            .size()
            .reset_index(
                name="salidas_tarimas"
            )
        )

    skus = set(
        inventory["sku"].astype(str)
    ) | set(
        exits["sku"].astype(str)
    )

    if not skus:
        return pd.DataFrame(
            columns=[
                "sku",
                "product",
                "inventario_actual_tarimas",
                "salidas_tarimas",
                "rotacion_operativa",
                "participacion_salidas_pct",
            ]
        )

    rows = []

    product_map = (
        catalog.set_index("sku")["product"]
        .to_dict()
        if not catalog.empty
        else {}
    )

    for sku in sorted(skus):
        inv_match = inventory[
            inventory["sku"].astype(str) == str(sku)
        ]

        exit_match = exits[
            exits["sku"].astype(str) == str(sku)
        ]

        current_pallets = (
            int(inv_match.iloc[0]["tarimas"])
            if not inv_match.empty
            else 0
        )

        exit_pallets = (
            int(exit_match.iloc[0]["salidas_tarimas"])
            if not exit_match.empty
            else 0
        )

        if not inv_match.empty:
            product_name = inv_match.iloc[0]["product"]
        else:
            product_name = product_map.get(
                str(sku).strip().upper(),
                "Sin nombre",
            )

        denominator = max(
            current_pallets,
            1,
        )

        rows.append(
            {
                "sku": sku,
                "product": product_name,
                "inventario_actual_tarimas": current_pallets,
                "salidas_tarimas": exit_pallets,
                "rotacion_operativa": exit_pallets / denominator,
            }
        )

    result = pd.DataFrame(rows)

    total_exits = int(
        result["salidas_tarimas"].sum()
    )

    result["participacion_salidas_pct"] = (
        result["salidas_tarimas"]
        / total_exits
        * 100
        if total_exits > 0
        else 0
    )

    return result.sort_values(
        [
            "salidas_tarimas",
            "rotacion_operativa",
        ],
        ascending=False,
    )


# ============================================================
# DATOS
# ============================================================

def distribute_row_lengths(
    capacity: int,
    rows_count: int,
):
    """
    Distribuye exactamente la capacidad declarada entre las filas.
    Ejemplo: 25 tarimas / 3 filas -> [9, 8, 8].
    """
    base = capacity // rows_count
    remainder = capacity % rows_count

    return [
        base + (1 if i < remainder else 0)
        for i in range(rows_count)
    ]


def create_empty_state() -> pd.DataFrame:
    rows = []

    for zone_name, cfg in ZONES.items():
        counter = 1

        row_lengths = distribute_row_lengths(
            cfg["capacity_positions"],
            cfg["rows"],
        )

        for row_num, row_length in enumerate(
            row_lengths,
            start=1,
        ):
            row_id = f'F{row_num:02d}'

            for depth in range(
                1,
                row_length + 1,
            ):
                position = f'{cfg["prefix"]}{counter:03d}'

                # Nivel 1 = capacidad declarada.
                # Niveles 2 y 3 = remontado eventual / sobreproducción.
                for level in range(
                    1,
                    MAX_LEVELS + 1,
                ):
                    rows.append(
                        {
                            "zone": zone_name,
                            "row_id": row_id,
                            "depth": depth,
                            "position": position,
                            "level": level,
                            "sku": "",
                            "product": "",
                            "lot": "",
                            "production_date": "",
                            "entry_shift": "",
                            "bundles": 0,
                            "status": "Disponible",
                            "last_update": "",
                        }
                    )

                counter += 1

    result = pd.DataFrame(
        rows,
        columns=STATE_COLUMNS,
    )

    physical_positions = (
        result[
            ["zone", "position"]
        ]
        .drop_duplicates()
        .shape[0]
    )

    if physical_positions != DECLARED_CAPACITY:
        raise ValueError(
            f"Configuración inválida: "
            f"{physical_positions} posiciones base; "
            f"se esperaban {DECLARED_CAPACITY}."
        )

    return result


def save_state(df: pd.DataFrame) -> None:
    df.to_csv(STATE_FILE, index=False, encoding="utf-8-sig")


def load_state() -> pd.DataFrame:
    if not STATE_FILE.exists():
        df = create_empty_state()
        save_state(df)
        return df

    df = pd.read_csv(STATE_FILE, dtype=str).fillna("")

    defaults = {
        "zone": "",
        "row_id": "",
        "depth": 1,
        "position": "",
        "level": 1,
        "sku": "",
        "product": "",
        "lot": "",
        "production_date": "",
        "entry_shift": "",
        "bundles": 0,
        "status": "Disponible",
        "last_update": "",
    }

    for col, default in defaults.items():
        if col not in df.columns:
            df[col] = default

    for col in ["depth", "level", "bundles"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    return df[STATE_COLUMNS]


def save_moves(df: pd.DataFrame) -> None:
    df.to_csv(MOVES_FILE, index=False, encoding="utf-8-sig")


def load_moves() -> pd.DataFrame:
    if not MOVES_FILE.exists():
        save_moves(pd.DataFrame(columns=MOVE_COLUMNS))

    df = pd.read_csv(MOVES_FILE, dtype=str).fillna("")

    for col in MOVE_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    return df[MOVE_COLUMNS]


def log_move(**kwargs) -> None:
    moves = load_moves()

    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "shift": kwargs.get("shift", ""),
        "movement_type": kwargs.get("movement_type", ""),
        "origin": kwargs.get("origin", ""),
        "destination": kwargs.get("destination", ""),
        "zone_origin": kwargs.get("zone_origin", ""),
        "zone_destination": kwargs.get("zone_destination", ""),
        "row_origin": kwargs.get("row_origin", ""),
        "row_destination": kwargs.get("row_destination", ""),
        "sku": kwargs.get("sku", ""),
        "product": kwargs.get("product", ""),
        "lot": kwargs.get("lot", ""),
        "production_date": kwargs.get("production_date", ""),
        "bundles": kwargs.get("bundles", 0),
        "notes": kwargs.get("notes", ""),
    }

    moves = pd.concat([moves, pd.DataFrame([row])], ignore_index=True)
    save_moves(moves)


def occupy_slot(
    df: pd.DataFrame,
    idx: int,
    sku: str,
    product: str,
    lot: str,
    production_date: str,
    entry_shift: str,
    bundles: int,
) -> None:
    df.at[idx, "sku"] = sku.strip()
    df.at[idx, "product"] = product.strip()
    df.at[idx, "lot"] = lot.strip()
    df.at[idx, "production_date"] = production_date
    df.at[idx, "entry_shift"] = entry_shift
    df.at[idx, "bundles"] = int(bundles)
    df.at[idx, "status"] = "Ocupada"
    df.at[idx, "last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def clear_slot(df: pd.DataFrame, idx: int) -> None:
    for col in [
        "sku",
        "product",
        "lot",
        "production_date",
        "entry_shift",
        "last_update",
    ]:
        df.at[idx, col] = ""

    df.at[idx, "bundles"] = 0
    df.at[idx, "status"] = "Disponible"


# ============================================================
# REGLAS DE UBICACIÓN / REMONTADO
# ============================================================

def slot_row(df, zone, position, level):
    return df[
        (df["zone"] == zone)
        & (df["position"] == position)
        & (df["level"] == int(level))
    ]


def can_place_on_level(df, zone, position, level) -> bool:
    current = slot_row(df, zone, position, level)

    if current.empty or current.iloc[0]["status"] != "Disponible":
        return False

    if int(level) == 1:
        return True

    lower = df[
        (df["zone"] == zone)
        & (df["position"] == position)
        & (df["level"] < int(level))
    ]

    return not lower.empty and (lower["status"] == "Ocupada").all()


def top_occupied_level(df, zone, position):
    pos = df[
        (df["zone"] == zone)
        & (df["position"] == position)
        & (df["status"] == "Ocupada")
    ]

    if pos.empty:
        return None

    return int(pos["level"].max())


def can_remove(df, zone, position, level) -> bool:
    top = top_occupied_level(df, zone, position)
    return top is not None and int(level) == top


def count_above(df, zone, position, level) -> int:
    return int(
        (
            (
                (df["zone"] == zone)
                & (df["position"] == position)
                & (df["level"] > int(level))
                & (df["status"] == "Ocupada")
            )
        ).sum()
    )


def accessible_slots_for_relocation(df):
    occupied = df[df["status"] == "Ocupada"].copy()

    if occupied.empty:
        return occupied

    mask = occupied.apply(
        lambda r: can_remove(
            df,
            r["zone"],
            r["position"],
            int(r["level"]),
        ),
        axis=1,
    )

    return occupied[mask].copy()


def valid_destinations(df, zone):
    zone_df = df[df["zone"] == zone].copy()

    valid = []

    for idx, row in zone_df.iterrows():
        if can_place_on_level(
            df,
            zone,
            row["position"],
            int(row["level"]),
        ):
            valid.append(idx)

    return df.loc[valid].copy()



# ============================================================
# REGLA: UNA FILA = UN SOLO SKU
# ============================================================

def row_assignment(
    df: pd.DataFrame,
    zone: str,
    row_id: str,
):
    occupied = df[
        (df["zone"] == zone)
        & (df["row_id"] == row_id)
        & (df["status"] == "Ocupada")
    ].copy()

    if occupied.empty:
        return None

    occupied["sku_clean"] = (
        occupied["sku"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    occupied = occupied[
        occupied["sku_clean"] != ""
    ]

    if occupied.empty:
        return None

    skus = sorted(
        occupied["sku_clean"]
        .unique()
        .tolist()
    )

    product_map = {}

    for sku_value in skus:
        product_rows = occupied[
            occupied["sku_clean"] == sku_value
        ]

        product_name = ""

        if not product_rows.empty:
            product_name = str(
                product_rows.iloc[0]["product"]
            ).strip()

        product_map[sku_value] = product_name

    return {
        "skus": skus,
        "products": product_map,
        "mixed": len(skus) > 1,
        "primary_sku": skus[0],
    }


def row_accepts_sku(
    df: pd.DataFrame,
    zone: str,
    row_id: str,
    sku: str,
) -> bool:
    assignment = row_assignment(
        df,
        zone,
        row_id,
    )

    if assignment is None:
        return True

    if assignment["mixed"]:
        return False

    sku_clean = str(sku).strip().upper()

    return (
        sku_clean
        == assignment["primary_sku"]
    )


def row_assignment_text(
    df: pd.DataFrame,
    zone: str,
    row_id: str,
) -> str:
    assignment = row_assignment(
        df,
        zone,
        row_id,
    )

    if assignment is None:
        return "Fila libre"

    if assignment["mixed"]:
        return (
            "FILA CON SKU MEZCLADOS: "
            + ", ".join(
                assignment["skus"]
            )
        )

    sku = assignment["primary_sku"]
    product = assignment[
        "products"
    ].get(
        sku,
        "",
    )

    if product:
        return (
            f"SKU {sku} — {product}"
        )

    return f"SKU {sku}"


def valid_destinations_for_sku(
    df: pd.DataFrame,
    zone: str,
    sku: str,
) -> pd.DataFrame:
    valid = valid_destinations(
        df,
        zone,
    )

    if valid.empty:
        return valid

    valid = valid[
        valid.apply(
            lambda r: row_accepts_sku(
                df,
                zone,
                r["row_id"],
                sku,
            ),
            axis=1,
        )
    ].copy()

    return valid


def mixed_rows_table(
    df: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    unique_rows = (
        df[
            ["zone", "row_id"]
        ]
        .drop_duplicates()
    )

    for _, row in unique_rows.iterrows():
        assignment = row_assignment(
            df,
            row["zone"],
            row["row_id"],
        )

        if (
            assignment is not None
            and assignment["mixed"]
        ):
            rows.append(
                {
                    "Zona": row["zone"],
                    "Fila": row["row_id"],
                    "SKU presentes": ", ".join(
                        assignment["skus"]
                    ),
                }
            )

    return pd.DataFrame(rows)


# ============================================================
# PEPS / ACCESO POR UN EXTREMO
# ============================================================

def pallets_in_front(df, zone, row_id, depth) -> pd.DataFrame:
    """
    Profundidad 1 = cerca del acceso.
    Para llegar a profundidad d hay que liberar posiciones anteriores
    cuando están ocupadas.
    """
    return df[
        (df["zone"] == zone)
        & (df["row_id"] == row_id)
        & (df["depth"] < int(depth))
        & (df["status"] == "Ocupada")
    ].copy()


def front_positions_count(df, zone, row_id, depth) -> int:
    front = pallets_in_front(df, zone, row_id, depth)
    return front[["position"]].drop_duplicates().shape[0]


def front_pallets_count(df, zone, row_id, depth) -> int:
    return len(pallets_in_front(df, zone, row_id, depth))


def access_blocking_count(df, row) -> int:
    """
    Tarimas que están delante de la posición + tarimas encima.
    """
    front = front_pallets_count(
        df,
        row["zone"],
        row["row_id"],
        int(row["depth"]),
    )

    above = count_above(
        df,
        row["zone"],
        row["position"],
        int(row["level"]),
    )

    return front + above


def peps_sequence_for_sku(df, zone, row_id, sku):
    """
    Obtiene tarimas de un SKU en la fila, en orden desde el acceso al fondo,
    considerando primero profundidad y luego nivel.
    """
    work = df[
        (df["zone"] == zone)
        & (df["row_id"] == row_id)
        & (df["sku"].str.upper() == sku.upper())
        & (df["status"] == "Ocupada")
    ].copy()

    if work.empty:
        return work

    work["parsed_date"] = pd.to_datetime(
        work["production_date"],
        errors="coerce",
    )

    return work.sort_values(
        ["depth", "level"],
        ascending=[True, True],
    )


def peps_is_ordered(df, zone, row_id, sku):
    seq = peps_sequence_for_sku(df, zone, row_id, sku)

    if len(seq) <= 1:
        return True

    dates = seq["parsed_date"].dropna().tolist()

    if len(dates) <= 1:
        return True

    return dates == sorted(dates)


def recommended_peps_table(df, zone, row_id, sku):
    seq = peps_sequence_for_sku(df, zone, row_id, sku)

    if seq.empty:
        return seq

    seq = seq.copy()

    valid = seq.dropna(subset=["parsed_date"]).sort_values(
        "parsed_date",
        ascending=True,
    )

    invalid = seq[seq["parsed_date"].isna()]

    ordered_lots = pd.concat([valid, invalid], ignore_index=True)

    locations = seq[
        ["position", "level", "depth"]
    ].sort_values(
        ["depth", "level"]
    ).reset_index(drop=True)

    rec = ordered_lots[
        [
            "sku",
            "product",
            "lot",
            "production_date",
            "bundles",
        ]
    ].reset_index(drop=True)

    rec = pd.concat([locations, rec], axis=1)

    return rec


def recommend_deepest_destination(
    df,
    zone,
    row_id,
    sku,
):
    """
    Recomendación PEPS con prioridad de niveles:

    1. Primero completar Nivel 1.
    2. Luego completar Nivel 2.
    3. Nivel 3 solo se permite cuando TODA la fila tiene N1 y N2 ocupados.

    Dentro del nivel permitido se recomienda la posición más profunda,
    para mantener producto nuevo hacia el fondo.
    """
    if not row_accepts_sku(
        df,
        zone,
        row_id,
        sku,
    ):
        return None

    row_df = df[
        (df["zone"] == zone)
        & (df["row_id"] == row_id)
    ].copy()

    if row_df.empty:
        return None

    # NIVEL 1: completar primero.
    level1 = row_df[
        row_df["level"] == 1
    ].copy()

    free_level1 = level1[
        level1["status"] == "Disponible"
    ].copy()

    if not free_level1.empty:
        return (
            free_level1
            .sort_values(
                "depth",
                ascending=False,
            )
            .iloc[0]
        )

    # NIVEL 2: solo cuando N1 ya no tiene espacios libres.
    level2_valid = []

    for idx, row in row_df[
        row_df["level"] == 2
    ].iterrows():
        if can_place_on_level(
            df,
            zone,
            row["position"],
            2,
        ):
            level2_valid.append(idx)

    if level2_valid:
        return (
            df.loc[
                level2_valid
            ]
            .sort_values(
                "depth",
                ascending=False,
            )
            .iloc[0]
        )

    # NIVEL 3: solo si TODA la fila tiene N1 y N2 ocupados.
    positions = (
        row_df[
            ["position"]
        ]
        .drop_duplicates()
        ["position"]
        .tolist()
    )

    all_n1_n2_full = True

    for position in positions:
        first_two = row_df[
            (row_df["position"] == position)
            & (
                row_df["level"]
                .isin(
                    [1, 2]
                )
            )
        ]

        if (
            len(first_two) < 2
            or not (
                first_two["status"]
                == "Ocupada"
            ).all()
        ):
            all_n1_n2_full = False
            break

    if not all_n1_n2_full:
        return None

    level3_valid = []

    for idx, row in row_df[
        row_df["level"] == 3
    ].iterrows():
        if can_place_on_level(
            df,
            zone,
            row["position"],
            3,
        ):
            level3_valid.append(idx)

    if not level3_valid:
        return None

    return (
        df.loc[
            level3_valid
        ]
        .sort_values(
            "depth",
            ascending=False,
        )
        .iloc[0]
    )


def row_level_status(
    df,
    zone,
    row_id,
):
    row_df = df[
        (df["zone"] == zone)
        & (df["row_id"] == row_id)
    ]

    level1 = row_df[
        row_df["level"] == 1
    ]

    level2 = row_df[
        row_df["level"] == 2
    ]

    n1_free = int(
        (
            level1["status"]
            == "Disponible"
        ).sum()
    )

    n2_free = int(
        (
            level2["status"]
            == "Disponible"
        ).sum()
    )

    n1_full = (
        not level1.empty
        and n1_free == 0
    )

    n2_full = (
        not level2.empty
        and n2_free == 0
    )

    return {
        "n1_free": n1_free,
        "n2_free": n2_free,
        "n1_full": n1_full,
        "n2_full": n2_full,
        "n3_allowed": (
            n1_full
            and n2_full
        ),
    }



# ============================================================
# ENTRADA MÚLTIPLE / PLANIFICACIÓN DE UBICACIONES
# ============================================================

def plan_batch_entry(
    df: pd.DataFrame,
    zone: str,
    row_id: str,
    sku: str,
    quantity: int,
) -> pd.DataFrame:
    """
    Simula el ingreso de varias tarimas del mismo SKU/lote sin modificar
    el inventario real.

    Respeta:
    - una fila = un SKU;
    - PEPS: producto nuevo hacia el fondo;
    - prioridad N1 -> N2;
    - N3 solo cuando toda la fila tenga N1 y N2 ocupados.
    """
    quantity = int(quantity)

    if quantity <= 0:
        return pd.DataFrame()

    if not row_accepts_sku(
        df,
        zone,
        row_id,
        sku,
    ):
        return pd.DataFrame()

    simulated = df.copy()
    planned = []

    for pallet_number in range(
        1,
        quantity + 1,
    ):
        rec = recommend_deepest_destination(
            simulated,
            zone,
            row_id,
            sku,
        )

        if rec is None:
            break

        idx = rec.name

        planned.append(
            {
                "Tarima": pallet_number,
                "Zona": zone,
                "Fila": row_id,
                "Posición": rec["position"],
                "Profundidad": int(rec["depth"]),
                "Nivel": int(rec["level"]),
            }
        )

        # Ocupación simulada mínima para que la siguiente recomendación
        # respete el nivel anterior.
        simulated.at[
            idx,
            "status"
        ] = "Ocupada"

        simulated.at[
            idx,
            "sku"
        ] = sku

    return pd.DataFrame(
        planned
    )


def history_excel_bytes(
    moves_df: pd.DataFrame,
    state_df: pd.DataFrame,
) -> bytes:
    """
    Crea un Excel empresarial con Historial + Resumen.
    """
    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter",
    ) as writer:
        workbook = writer.book

        # Colores sobrios de empresa
        title_fmt = workbook.add_format(
            {
                "bold": True,
                "font_size": 18,
                "font_color": "#FFFFFF",
                "bg_color": "#1F4E78",
                "align": "left",
                "valign": "vcenter",
            }
        )

        subtitle_fmt = workbook.add_format(
            {
                "font_size": 10,
                "font_color": "#595959",
            }
        )

        header_fmt = workbook.add_format(
            {
                "bold": True,
                "font_color": "#FFFFFF",
                "bg_color": "#2F75B5",
                "border": 1,
                "align": "center",
                "valign": "vcenter",
            }
        )

        kpi_label_fmt = workbook.add_format(
            {
                "bold": True,
                "font_color": "#1F1F1F",
                "bg_color": "#D9EAF7",
                "border": 1,
            }
        )

        kpi_value_fmt = workbook.add_format(
            {
                "bold": True,
                "font_size": 12,
                "align": "center",
                "border": 1,
            }
        )

        percent_fmt = workbook.add_format(
            {
                "num_format": "0.0%",
                "align": "center",
                "border": 1,
            }
        )

        # ----------------------------------------------------
        # HOJA HISTORIAL
        # ----------------------------------------------------
        history_export = moves_df.copy()

        rename_map = {
            "timestamp": "Fecha y hora",
            "shift": "Turno",
            "movement_type": "Movimiento",
            "origin": "Origen",
            "destination": "Destino",
            "zone_origin": "Zona origen",
            "zone_destination": "Zona destino",
            "row_origin": "Fila origen",
            "row_destination": "Fila destino",
            "sku": "SKU",
            "product": "Producto",
            "lot": "Lote",
            "production_date": "Fecha producción",
            "bundles": "Bultos",
            "notes": "Observaciones",
        }

        history_export = history_export.rename(
            columns=rename_map
        )

        history_export.to_excel(
            writer,
            sheet_name="Historial",
            startrow=3,
            index=False,
        )

        ws = writer.sheets[
            "Historial"
        ]

        last_col = max(
            len(history_export.columns) - 1,
            0,
        )

        ws.merge_range(
            0,
            0,
            0,
            last_col,
            "Historial de movimientos — COONAPROSAL",
            title_fmt,
        )

        ws.write(
            1,
            0,
            "Generado:",
            subtitle_fmt,
        )

        ws.write(
            1,
            1,
            datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            ),
            subtitle_fmt,
        )

        for col_num, col_name in enumerate(
            history_export.columns
        ):
            ws.write(
                3,
                col_num,
                col_name,
                header_fmt,
            )

        if not history_export.empty:
            ws.add_table(
                3,
                0,
                3 + len(history_export),
                last_col,
                {
                    "name": "TablaHistorial",
                    "style": "Table Style Medium 2",
                    "columns": [
                        {
                            "header": col
                        }
                        for col
                        in history_export.columns
                    ],
                },
            )

        ws.freeze_panes(
            4,
            0,
        )

        widths = {
            "Fecha y hora": 20,
            "Turno": 12,
            "Movimiento": 18,
            "Origen": 14,
            "Destino": 14,
            "Zona origen": 28,
            "Zona destino": 28,
            "Fila origen": 12,
            "Fila destino": 12,
            "SKU": 12,
            "Producto": 38,
            "Lote": 14,
            "Fecha producción": 18,
            "Bultos": 12,
            "Observaciones": 55,
        }

        for col_num, col_name in enumerate(
            history_export.columns
        ):
            ws.set_column(
                col_num,
                col_num,
                widths.get(
                    col_name,
                    18,
                ),
            )


        # ----------------------------------------------------
        # HOJA RESUMEN
        # ----------------------------------------------------
        summary_ws = workbook.add_worksheet(
            "Resumen"
        )

        summary_ws.merge_range(
            "A1:F1",
            "Resumen de movimientos — COONAPROSAL",
            title_fmt,
        )

        total_moves = len(
            moves_df
        )

        entries = int(
            moves_df[
                "movement_type"
            ]
            .astype(str)
            .str.contains(
                "Entrada",
                case=False,
                na=False,
            )
            .sum()
        ) if not moves_df.empty else 0

        exits = int(
            moves_df[
                "movement_type"
            ]
            .astype(str)
            .str.contains(
                "Salida",
                case=False,
                na=False,
            )
            .sum()
        ) if not moves_df.empty else 0

        relocations = int(
            moves_df[
                "movement_type"
            ]
            .astype(str)
            .str.contains(
                "Relocal",
                case=False,
                na=False,
            )
            .sum()
        ) if not moves_df.empty else 0

        current_pallets = int(
            (
                state_df[
                    "status"
                ]
                == "Ocupada"
            ).sum()
        )

        summary_data = [
            (
                "Total de movimientos",
                total_moves,
            ),
            (
                "Entradas registradas",
                entries,
            ),
            (
                "Salidas registradas",
                exits,
            ),
            (
                "Relocalizaciones",
                relocations,
            ),
            (
                "Tarimas actuales",
                current_pallets,
            ),
        ]

        summary_ws.write(
            "A3",
            "Indicador",
            header_fmt,
        )
        summary_ws.write(
            "B3",
            "Valor",
            header_fmt,
        )

        for row_num, (
            label,
            value,
        ) in enumerate(
            summary_data,
            start=3,
        ):
            summary_ws.write(
                row_num,
                0,
                label,
                kpi_label_fmt,
            )
            summary_ws.write(
                row_num,
                1,
                value,
                kpi_value_fmt,
            )

        summary_ws.set_column(
            "A:A",
            30,
        )
        summary_ws.set_column(
            "B:B",
            16,
        )

        # Resumen por tipo de movimiento
        if not moves_df.empty:
            counts = (
                moves_df[
                    "movement_type"
                ]
                .value_counts()
                .reset_index()
            )

            counts.columns = [
                "Movimiento",
                "Cantidad",
            ]

            counts.to_excel(
                writer,
                sheet_name="Resumen",
                startrow=10,
                startcol=0,
                index=False,
            )

            for col_num, col_name in enumerate(
                counts.columns
            ):
                summary_ws.write(
                    10,
                    col_num,
                    col_name,
                    header_fmt,
                )

            chart = workbook.add_chart(
                {
                    "type": "column"
                }
            )

            chart.add_series(
                {
                    "name": "Movimientos",
                    "categories": [
                        "Resumen",
                        11,
                        0,
                        10 + len(counts),
                        0,
                    ],
                    "values": [
                        "Resumen",
                        11,
                        1,
                        10 + len(counts),
                        1,
                    ],
                }
            )

            chart.set_title(
                {
                    "name": "Movimientos por tipo"
                }
            )

            chart.set_legend(
                {
                    "none": True
                }
            )

            chart.set_style(
                10
            )

            summary_ws.insert_chart(
                "D3",
                chart,
                {
                    "x_scale": 1.15,
                    "y_scale": 1.15,
                },
            )

    output.seek(0)
    return output.getvalue()


# ============================================================
# ASIGNACIÓN AUTOMÁTICA POR FILAS
# ============================================================

def row_sort_key(row_id: str):
    try:
        return int(str(row_id).replace("F", ""))
    except Exception:
        return 999999


def compatible_rows_for_sku(
    df: pd.DataFrame,
    zone: str,
    sku: str,
):
    """
    Prioriza filas que ya contienen el mismo SKU.
    Después usa filas completamente libres.
    Excluye filas asignadas a otro SKU.
    """
    rows = sorted(
        df[df["zone"] == zone]["row_id"].unique(),
        key=row_sort_key,
    )

    same_sku = []
    empty_rows = []

    for row_id in rows:
        assignment = row_assignment(
            df,
            zone,
            row_id,
        )

        if assignment is None:
            empty_rows.append(row_id)
        elif (
            not assignment["mixed"]
            and assignment["primary_sku"]
            == str(sku).strip().upper()
        ):
            same_sku.append(row_id)

    return same_sku + empty_rows


def next_slot_in_row(
    df: pd.DataFrame,
    zone: str,
    row_id: str,
    allow_level3: bool = False,
):
    """
    Busca una sola ubicación en la fila:
    N1 -> N2 -> N3 (solo si allow_level3=True).
    Dentro de cada nivel prioriza el fondo de la fila.
    """
    row_df = df[
        (df["zone"] == zone)
        & (df["row_id"] == row_id)
    ].copy()

    if row_df.empty:
        return None

    # Nivel 1
    level1 = row_df[
        (row_df["level"] == 1)
        & (row_df["status"] == "Disponible")
    ].sort_values(
        "depth",
        ascending=False,
    )

    if not level1.empty:
        return level1.iloc[0]

    # Nivel 2
    level2_indices = []

    for idx, row in row_df[
        row_df["level"] == 2
    ].iterrows():
        if can_place_on_level(
            df,
            zone,
            row["position"],
            2,
        ):
            level2_indices.append(idx)

    if level2_indices:
        return (
            df.loc[level2_indices]
            .sort_values(
                "depth",
                ascending=False,
            )
            .iloc[0]
        )

    # Nivel 3 solo con autorización expresa
    if not allow_level3:
        return None

    level3_indices = []

    for idx, row in row_df[
        row_df["level"] == 3
    ].iterrows():
        if can_place_on_level(
            df,
            zone,
            row["position"],
            3,
        ):
            level3_indices.append(idx)

    if not level3_indices:
        return None

    return (
        df.loc[level3_indices]
        .sort_values(
            "depth",
            ascending=False,
        )
        .iloc[0]
    )


def plan_batch_entry_across_rows(
    df: pd.DataFrame,
    zone: str,
    sku: str,
    quantity: int,
    allow_level3: bool = False,
) -> pd.DataFrame:
    """
    Asignación normal:
      Fila 1 -> completar N1 -> completar N2 -> pasar a Fila 2.
    N3 no se usa en la primera pasada.

    Si allow_level3=True y todavía faltan tarimas después de utilizar
    N1+N2 de todas las filas compatibles, se realiza una segunda pasada
    usando N3 como sobrealmacenamiento extraordinario.
    """
    quantity = int(quantity)

    if quantity <= 0:
        return pd.DataFrame()

    simulated = df.copy()
    planned = []
    rows = compatible_rows_for_sku(
        simulated,
        zone,
        sku,
    )

    # Primera pasada: SOLO N1 y N2 por fila, terminando una fila antes de la siguiente.
    for row_id in rows:
        while len(planned) < quantity:
            rec = next_slot_in_row(
                simulated,
                zone,
                row_id,
                allow_level3=False,
            )

            if rec is None:
                break

            idx = rec.name

            planned.append(
                {
                    "Tarima": len(planned) + 1,
                    "Zona": zone,
                    "Fila": row_id,
                    "Posición": rec["position"],
                    "Profundidad": int(rec["depth"]),
                    "Nivel": int(rec["level"]),
                    "Tipo de ubicación": "Normal",
                }
            )

            simulated.at[idx, "status"] = "Ocupada"
            simulated.at[idx, "sku"] = sku

        if len(planned) >= quantity:
            break

    # Segunda pasada: N3 únicamente si fue autorizado explícitamente.
    if (
        len(planned) < quantity
        and allow_level3
    ):
        rows = compatible_rows_for_sku(
            simulated,
            zone,
            sku,
        )

        for row_id in rows:
            while len(planned) < quantity:
                row_df = simulated[
                    (simulated["zone"] == zone)
                    & (simulated["row_id"] == row_id)
                ]

                # En sobrealmacenamiento solo buscamos N3.
                level3_indices = []

                for idx, row in row_df[
                    row_df["level"] == 3
                ].iterrows():
                    if can_place_on_level(
                        simulated,
                        zone,
                        row["position"],
                        3,
                    ):
                        level3_indices.append(idx)

                if not level3_indices:
                    break

                rec = (
                    simulated.loc[level3_indices]
                    .sort_values(
                        "depth",
                        ascending=False,
                    )
                    .iloc[0]
                )

                idx = rec.name

                planned.append(
                    {
                        "Tarima": len(planned) + 1,
                        "Zona": zone,
                        "Fila": row_id,
                        "Posición": rec["position"],
                        "Profundidad": int(rec["depth"]),
                        "Nivel": 3,
                        "Tipo de ubicación": "Sobrealmacenamiento N3",
                    }
                )

                simulated.at[idx, "status"] = "Ocupada"
                simulated.at[idx, "sku"] = sku

            if len(planned) >= quantity:
                break

    return pd.DataFrame(planned)


def direct_accessible_pallets_in_row(
    df: pd.DataFrame,
    zone: str,
    row_id: str,
) -> pd.DataFrame:
    """
    Tarimas que pueden moverse directamente:
    - están en el nivel superior de su posición;
    - no tienen posiciones ocupadas delante.
    """
    work = df[
        (df["zone"] == zone)
        & (df["row_id"] == row_id)
        & (df["status"] == "Ocupada")
    ].copy()

    if work.empty:
        return work

    mask = work.apply(
        lambda r: (
            can_remove(
                df,
                zone,
                r["position"],
                int(r["level"]),
            )
            and front_pallets_count(
                df,
                zone,
                row_id,
                int(r["depth"]),
            ) == 0
        ),
        axis=1,
    )

    return work[mask].copy()


def relocation_destination_slot(
    df: pd.DataFrame,
    zone: str,
    row_id: str,
    sku: str,
    allow_level3: bool = False,
):
    if not row_accepts_sku(
        df,
        zone,
        row_id,
        sku,
    ):
        return None

    return next_slot_in_row(
        df,
        zone,
        row_id,
        allow_level3=allow_level3,
    )


def pallet_drag_label(
    idx,
    row,
):
    """
    Etiqueta visible de la tarima.
    No muestra el ID interno para que la interfaz sea más clara.
    """
    return (
        f"{row['position']}-N{row['level']} · "
        f"SKU {row['sku']} · Lote {row['lot']} · "
        f"Fecha {row['production_date'] or 's/f'}"
    )


def pallet_drag_key(
    row,
):
    """
    Clave visible y única por ubicación física.
    """
    return f"{row['position']}-N{row['level']}"

# ============================================================
# COLORES Y MAPA VISUAL
# ============================================================

def lot_palette(matches):
    if matches.empty:
        return {}, None

    work = matches.copy()
    work["parsed_date"] = pd.to_datetime(
        work["production_date"],
        errors="coerce",
    )

    lot_dates = (
        work.groupby("lot", dropna=False)["parsed_date"]
        .min()
        .reset_index()
    )

    lot_dates["missing"] = lot_dates["parsed_date"].isna()

    lot_dates = lot_dates.sort_values(
        ["missing", "parsed_date", "lot"],
        ascending=[True, True, True],
    )

    palette = {}
    oldest = None

    for i, row in lot_dates.reset_index(drop=True).iterrows():
        lot = str(row["lot"])

        if i == 0 and not pd.isna(row["parsed_date"]):
            oldest = lot
            palette[lot] = "#F87171"
        else:
            palette[lot] = LOT_COLORS[i % len(LOT_COLORS)]

    return palette, oldest


def esc(value):
    return html.escape(str(value if value is not None else ""))


def stack_card(position_df, search, palette, oldest_lot):
    position_df = position_df.sort_values("level")

    first = position_df.iloc[0]
    zone = first["zone"]
    position = first["position"]
    row_id = first["row_id"]
    depth = int(first["depth"])

    levels = []

    for level in [3, 2, 1]:
        row = position_df[position_df["level"] == level].iloc[0]

        free = row["status"] == "Disponible"
        blob = f'{row["sku"]} {row["lot"]} {row["product"]}'.lower()
        matched = bool(search) and search.lower() in blob

        bg = "#ECFDF5" if free else "#DBEAFE"
        border = "#A7F3D0" if free else "#93C5FD"
        fg = "#065F46" if free else "#1E3A8A"

        if matched and row["lot"] in palette:
            bg = palette[row["lot"]]
            border = "#475569"
            fg = "#111827"

        oldest = (
            matched
            and oldest_lot
            and row["lot"] == oldest_lot
        )

        if oldest:
            border = "#991B1B"

        sku = row["sku"] if row["sku"] else "LIBRE"
        lot = row["lot"] if row["lot"] else "—"

        badge = ""

        if oldest:
            above = count_above(
                df,
                zone,
                position,
                level,
            )
            front = front_pallets_count(
                df,
                zone,
                row_id,
                depth,
            )

            total_block = above + front

            if total_block > 0:
                badge = f"{total_block} bloqueo(s)"
            else:
                badge = "PRIORIDAD"

        levels.append(
            (
                '<div class="level" '
                f'style="background:{bg};border-color:{border};color:{fg};">'
                f'<div class="level-num">N{level}</div>'
                f'<div class="sku">{esc(sku)}</div>'
                f'<div class="lot">{("Lote " + esc(lot)) if not free else ""}</div>'
                f'<div class="badge">{esc(badge)}</div>'
                '</div>'
            )
        )

    return (
        '<div class="stack-card">'
        + "".join(levels)
        + (
            '<div class="position-label">'
            f'{esc(position)} <span>· P{depth}</span>'
            '</div></div>'
        )
    )


def row_visual_html(row_df, search, palette, oldest_lot):
    row_id = row_df.iloc[0]["row_id"]

    positions = (
        row_df[["position", "depth"]]
        .drop_duplicates()
        .sort_values("depth")
    )

    cards = []

    for _, pos in positions.iterrows():
        pos_df = row_df[
            row_df["position"] == pos["position"]
        ]
        cards.append(
            stack_card(
                pos_df,
                search,
                palette,
                oldest_lot,
            )
        )

    return (
        '<div class="warehouse-row">'
        '<div class="row-header">'
        f'<strong>{esc(row_id)}</strong>'
        '<span class="access-badge">ACCESO →</span>'
        f'<span class="row-assignment">{esc(row_assignment_text(df, row_df.iloc[0]["zone"], row_id))}</span>'
        '<span class="row-help">· más antiguo cerca del acceso · producto nuevo hacia el fondo</span>'
        '</div>'
        '<div class="row-scroll">'
        + "".join(cards)
        + '</div></div>'
    )


def render_row_visual(row_df, search, palette, oldest_lot):
    """
    Renderiza el mapa con components.html para evitar que Markdown
    interprete el HTML como un bloque de código.
    """
    html_body = row_visual_html(
        row_df,
        search,
        palette,
        oldest_lot,
    )

    document = (
        '<style>'
        '*{box-sizing:border-box;}'
        'body{margin:0;padding:0;font-family:Arial,sans-serif;background:transparent;}'
        '.warehouse-row{border:1px solid #CBD5E1;border-radius:12px;'
        'padding:10px;background:#F8FAFC;width:100%;}'
        '.row-header{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:8px;}'
        '.row-header strong{font-size:13px;color:#0F172A;}'
        '.access-badge{background:#111827;color:#fff;padding:5px 10px;'
        'border-radius:999px;font-size:10px;font-weight:700;}'
        '.row-assignment{background:#E2E8F0;color:#334155;padding:4px 8px;border-radius:999px;font-size:10px;font-weight:700;}''.row-help{color:#64748B;font-size:10px;}'
        '.row-scroll{display:flex;gap:6px;overflow-x:auto;padding-bottom:6px;}'
        '.stack-card{min-width:88px;width:88px;border:2px solid #64748B;'
        'border-radius:9px;overflow:hidden;background:#fff;flex:0 0 auto;}'
        '.level{border-bottom:1px solid;min-height:54px;padding:5px 3px;'
        'display:flex;flex-direction:column;justify-content:center;text-align:center;}'
        '.level-num{font-size:8px;font-weight:700;opacity:.7;}'
        '.sku{font-size:11px;font-weight:800;line-height:1.2;}'
        '.lot{font-size:9px;line-height:1.2;}'
        '.badge{font-size:7px;font-weight:800;line-height:1.1;margin-top:2px;}'
        '.position-label{background:#0F172A;color:#fff;padding:5px 2px;'
        'text-align:center;font-size:10px;font-weight:800;}'
        '.position-label span{opacity:.65;font-weight:500;}'
        '</style>'
        + html_body
    )

    components.html(
        document,
        height=260,
        scrolling=False,
    )


# ============================================================
# APP
# ============================================================

df = load_state()
catalog = load_catalog()
moves = load_moves()

st.image(str(LOGO_PATH), width=160)

st.title("Almacén Digital — COONAPROSAL R.L.")

st.success(
    "VERSIÓN ACTIVA: V8.1 — relocalización visual por tarima"
)
st.caption(
    "Control visual de inventario, ubicación, remontado, lotes, indicadores y reacomodos PEPS. "
    "La profundidad 1 corresponde al lado de acceso de cada fila."
)


mixed_rows = mixed_rows_table(
    df
)

if not mixed_rows.empty:
    st.error(
        f"Se detectaron {len(mixed_rows)} fila(s) con SKU mezclados "
        "provenientes de registros anteriores. "
        "La V6.2 ya no permitirá crear nuevas mezclas."
    )

    with st.expander(
        "Ver filas que necesitan corrección"
    ):
        st.dataframe(
            mixed_rows,
            use_container_width=True,
            hide_index=True,
        )

# ============================================================
# PANEL GENERAL DE ESTADÍSTICAS E INDICADORES
# ============================================================

occupied_df = df[
    df["status"] == "Ocupada"
].copy()

stored_pallets = len(
    occupied_df
)

base_pallets = int(
    (
        occupied_df["level"] == 1
    ).sum()
)

remounted_pallets = int(
    (
        occupied_df["level"] > 1
    ).sum()
)

level2_pallets = int(
    (
        occupied_df["level"] == 2
    ).sum()
)

level3_pallets = int(
    (
        occupied_df["level"] == 3
    ).sum()
)

occupancy_pct = (
    stored_pallets
    / DECLARED_CAPACITY
    * 100
)

available_equivalent = max(
    DECLARED_CAPACITY
    - stored_pallets,
    0,
)

overcapacity = max(
    stored_pallets
    - DECLARED_CAPACITY,
    0,
)

available_pct = max(
    100 - occupancy_pct,
    0,
)

remounted_pct = (
    remounted_pallets
    / stored_pallets
    * 100
    if stored_pallets
    else 0
)

inventory_summary = current_inventory_summary(
    df,
    catalog,
)

rotation_summary = operational_rotation_table(
    df,
    moves,
    catalog,
)

st.divider()
st.subheader(
    "Panel general de inventario"
)

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric(
    "Capacidad declarada",
    f"{DECLARED_CAPACITY} tarimas",
)

k2.metric(
    "Tarimas actuales",
    stored_pallets,
)

k3.metric(
    "Ocupación",
    f"{occupancy_pct:.1f} %",
)

k4.metric(
    "Disponibles",
    available_equivalent,
)

k5.metric(
    "Tarimas remontadas",
    remounted_pallets,
)

k6.metric(
    "Sobrecapacidad",
    overcapacity,
)

st.progress(
    min(
        occupancy_pct / 100,
        1.0,
    )
)

if overcapacity > 0:
    st.error(
        f"Capacidad declarada excedida en {overcapacity} tarima(s). "
        f"Ocupación equivalente: {occupancy_pct:.1f} %."
    )
elif occupancy_pct >= 90:
    st.warning(
        f"Ocupación alta: {occupancy_pct:.1f} %. "
        f"Quedan {available_equivalent} tarimas de capacidad declarada."
    )
else:
    st.success(
        f"Ocupación dentro de capacidad declarada: {occupancy_pct:.1f} %."
    )

st.caption(
    f"Remontado actual: {remounted_pallets} tarima(s) "
    f"({remounted_pct:.1f} % del inventario). "
    f"Nivel 2: {level2_pallets} · Nivel 3: {level3_pallets}. "
    "Los niveles 2 y 3 se consideran remontado temporal, "
    "no capacidad normal adicional."
)

dash_tab1, dash_tab2, dash_tab3, dash_tab4 = st.tabs(
    [
        "Inventario actual",
        "Rotación y movimiento",
        "Consultar producto",
        "Ocupación por zona",
    ]
)

with dash_tab1:
    if inventory_summary.empty:
        st.info(
            "Todavía no hay inventario registrado."
        )
    else:
        left_chart, right_chart = st.columns(2)

        with left_chart:
            st.markdown(
                "#### Tarimas por producto"
            )

            st.bar_chart(
                inventory_summary[
                    [
                        "product",
                        "tarimas",
                    ]
                ].set_index(
                    "product"
                ),
                use_container_width=True,
            )

        with right_chart:
            st.markdown(
                "#### Participación del inventario (%)"
            )

            st.bar_chart(
                inventory_summary[
                    [
                        "product",
                        "participacion_tarimas_pct",
                    ]
                ].set_index(
                    "product"
                ),
                use_container_width=True,
            )

        inventory_display = (
            inventory_summary.copy()
        )

        inventory_display[
            "participacion_tarimas_pct"
        ] = inventory_display[
            "participacion_tarimas_pct"
        ].round(2)

        inventory_display = (
            inventory_display.rename(
                columns={
                    "sku": "SKU",
                    "product": "Producto",
                    "tarimas": "Tarimas actuales",
                    "bultos": "Bultos actuales",
                    "lotes": "Lotes",
                    "posiciones": "Posiciones utilizadas",
                    "participacion_tarimas_pct": "% del inventario",
                }
            )
        )

        st.dataframe(
            inventory_display,
            use_container_width=True,
            hide_index=True,
        )

with dash_tab2:
    st.caption(
        "Rotación operativa: salidas de tarimas registradas / "
        "inventario actual de tarimas. Es un indicador interno de movimiento, "
        "no la rotación financiera contable."
    )

    if rotation_summary.empty:
        st.info(
            "Aún no existen movimientos suficientes."
        )
    else:
        st.bar_chart(
            rotation_summary[
                [
                    "product",
                    "salidas_tarimas",
                ]
            ].set_index(
                "product"
            ),
            use_container_width=True,
        )

        rotation_display = (
            rotation_summary.copy()
        )

        rotation_display[
            "rotacion_operativa"
        ] = rotation_display[
            "rotacion_operativa"
        ].round(2)

        rotation_display[
            "participacion_salidas_pct"
        ] = rotation_display[
            "participacion_salidas_pct"
        ].round(2)

        st.dataframe(
            rotation_display.rename(
                columns={
                    "sku": "SKU",
                    "product": "Producto",
                    "inventario_actual_tarimas": "Inventario actual (tarimas)",
                    "salidas_tarimas": "Salidas registradas",
                    "rotacion_operativa": "Rotación operativa",
                    "participacion_salidas_pct": "% de las salidas",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

with dash_tab3:
    if inventory_summary.empty:
        st.info(
            "No hay productos con inventario."
        )
    else:
        selected_kpi_sku = st.selectbox(
            "Producto",
            inventory_summary[
                "sku"
            ].astype(str).tolist(),
            format_func=lambda sku: (
                f"{sku} — "
                f"{inventory_summary.loc[inventory_summary['sku'].astype(str) == str(sku), 'product'].iloc[0]}"
            ),
            key="dashboard_product_selector",
        )

        prod_inv = inventory_summary[
            inventory_summary[
                "sku"
            ].astype(str)
            == str(selected_kpi_sku)
        ].iloc[0]

        prod_rot_match = rotation_summary[
            rotation_summary[
                "sku"
            ].astype(str)
            == str(selected_kpi_sku)
        ]

        exits_value = (
            int(
                prod_rot_match.iloc[0][
                    "salidas_tarimas"
                ]
            )
            if not prod_rot_match.empty
            else 0
        )

        rotation_value = (
            float(
                prod_rot_match.iloc[0][
                    "rotacion_operativa"
                ]
            )
            if not prod_rot_match.empty
            else 0
        )

        p1, p2, p3, p4, p5 = st.columns(5)

        p1.metric(
            "Tarimas",
            int(prod_inv["tarimas"]),
        )
        p2.metric(
            "Bultos",
            int(prod_inv["bultos"]),
        )
        p3.metric(
            "Lotes",
            int(prod_inv["lotes"]),
        )
        p4.metric(
            "% inventario",
            f"{float(prod_inv['participacion_tarimas_pct']):.1f} %",
        )
        p5.metric(
            "Rotación operativa",
            f"{rotation_value:.2f}",
        )

        st.write(
            f"**Producto:** {prod_inv['product']} · "
            f"**Salidas registradas:** {exits_value} tarima(s)"
        )

with dash_tab4:
    zone_stats = []

    for zone_name, cfg in ZONES.items():
        zone_pallets = int(
            (
                (occupied_df["zone"] == zone_name)
            ).sum()
        )

        zone_capacity = int(
            cfg["capacity_positions"]
        )

        zone_pct = (
            zone_pallets
            / zone_capacity
            * 100
        )

        zone_stats.append(
            {
                "Zona": zone_name,
                "Capacidad declarada": zone_capacity,
                "Tarimas actuales": zone_pallets,
                "Ocupación %": round(
                    zone_pct,
                    1,
                ),
            }
        )

    zone_stats_df = pd.DataFrame(
        zone_stats
    )

    st.bar_chart(
        zone_stats_df[
            [
                "Zona",
                "Ocupación %",
            ]
        ].set_index(
            "Zona"
        ),
        use_container_width=True,
    )

    st.dataframe(
        zone_stats_df,
        use_container_width=True,
        hide_index=True,
    )

# ============================================================
# MAPA
# ============================================================

st.divider()
st.subheader("Vista visual del almacén")

m1, m2 = st.columns([1, 2])

with m1:
    selected_zone = st.selectbox(
        "Zona",
        list(ZONES.keys()),
    )

with m2:
    search = st.text_input(
        "Buscar SKU, lote o producto",
        placeholder="Ej.: 0002",
    ).strip()

zone_df = df[df["zone"] == selected_zone].copy()

available_rows_view = sorted(
    zone_df["row_id"].unique()
)

view_mode = st.radio(
    "Vista",
    [
        "Fila seleccionada",
        "Todas las filas",
    ],
    horizontal=True,
    key="map_view_mode",
)

selected_row_view = None

if view_mode == "Fila seleccionada":
    selected_row_view = st.selectbox(
        "Fila a visualizar",
        available_rows_view,
        key="map_row_selector",
    )

if search:
    matches = zone_df[
        zone_df.apply(
            lambda r: search.lower()
            in f'{r["sku"]} {r["lot"]} {r["product"]}'.lower(),
            axis=1,
        )
    ].copy()
else:
    matches = zone_df.iloc[0:0].copy()

palette, oldest_lot = lot_palette(matches)

st.markdown(
    "**Libre** &nbsp;&nbsp; **Ocupada** &nbsp;&nbsp; "
    "**Lote más antiguo / prioridad PEPS**",
    unsafe_allow_html=True,
)

if search and not matches.empty:
    lot_legend = []

    for lot, color in palette.items():
        label = f"Lote {lot}"

        if oldest_lot and lot == oldest_lot:
            label += " más antiguo"

        lot_legend.append(
            f"""
            <span style="
                display:inline-flex;
                align-items:center;
                gap:5px;
                margin-right:14px;
            ">
                <span style="
                    width:15px;height:15px;
                    background:{color};
                    border:1px solid #334155;
                    border-radius:3px;
                "></span>
                {esc(label)}
            </span>
            """
        )

    st.markdown(
        "".join(lot_legend),
        unsafe_allow_html=True,
    )

rows_to_render = (
    [selected_row_view]
    if view_mode == "Fila seleccionada"
    else sorted(
        zone_df["row_id"].unique()
    )
)

for row_id in rows_to_render:
    row_df = zone_df[
        zone_df["row_id"] == row_id
    ]

    render_row_visual(
        row_df,
        search,
        palette,
        oldest_lot,
    )

# ============================================================
# DIAGNÓSTICO PEPS DE BÚSQUEDA
# ============================================================

if search:
    st.markdown("### Resultado de búsqueda")

    if matches.empty:
        st.warning("No se encontraron coincidencias en esta zona.")
    else:
        result = matches.copy()

        result["tarimas_delante"] = result.apply(
            lambda r: front_pallets_count(
                df,
                r["zone"],
                r["row_id"],
                int(r["depth"]),
            ),
            axis=1,
        )

        result["tarimas_encima"] = result.apply(
            lambda r: count_above(
                df,
                r["zone"],
                r["position"],
                int(r["level"]),
            ),
            axis=1,
        )

        result["bloqueos_totales"] = (
            result["tarimas_delante"]
            + result["tarimas_encima"]
        )

        st.dataframe(
            result[
                [
                    "row_id",
                    "position",
                    "depth",
                    "level",
                    "sku",
                    "lot",
                    "production_date",
                    "tarimas_delante",
                    "tarimas_encima",
                    "bloqueos_totales",
                ]
            ].sort_values(
                [
                    "production_date",
                    "row_id",
                    "depth",
                    "level",
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )

        if oldest_lot:
            oldest = result[
                result["lot"] == oldest_lot
            ]

            blocks = int(oldest["bloqueos_totales"].min())

            if blocks == 0:
                st.success(
                    f"Lote prioritario {oldest_lot}: "
                    "existe al menos una tarima accesible."
                )
            else:
                st.warning(
                    f"Lote prioritario {oldest_lot}: "
                    f"mínimo {blocks} movimiento(s) de liberación "
                    "antes de acceder a una de sus tarimas."
                )

# ============================================================
# MOVIMIENTOS
# ============================================================

st.divider()
st.subheader("Operación")

tab_in, tab_out, tab_relocate, tab_peps = st.tabs(
    [
        "Entrada",
        "Salida",
        "Relocalizar",
        "Reacomodo PEPS",
    ]
)

# ============================================================
# ENTRADA MÚLTIPLE — AUTOMÁTICA POR FILAS
# ============================================================

with tab_in:
    turn_in = st.selectbox(
        "Turno",
        TURNOS,
        key="turn_in",
    )

    zone_in = st.selectbox(
        "Zona de ingreso",
        list(ZONES.keys()),
        key="zone_in",
    )

    assign_mode = st.radio(
        "Modo de ubicación",
        [
            "PEPS automático por filas",
            "Manual",
        ],
        horizontal=True,
        key="assign_mode",
    )

    sku = st.text_input(
        "Código SKU",
        placeholder="Ej.: 0002",
        key="entry_sku",
    ).strip().upper()

    product_info = lookup_product(
        catalog,
        sku,
    )

    if product_info:
        product = product_info["product"]

        st.success(
            f"Producto identificado: **{product}**"
        )

        st.caption(
            f"Tipo: {product_info.get('category') or 'Sin clasificar'} "
            f"· Unidad: {product_info.get('unit') or 'Bultos'} "
            f"· Zona sugerida: {product_info.get('suggested_zone') or 'Sin asignación fija'}"
        )

        compatible = compatible_rows_for_sku(
            df,
            zone_in,
            sku,
        )

        st.info(
            f"Filas compatibles disponibles para este SKU: "
            f"{', '.join(compatible) if compatible else 'ninguna'}"
        )
    else:
        product = ""

        if sku:
            st.warning(
                "SKU no encontrado en catálogo. "
                "Puede ingresar el nombre para guardarlo."
            )

    manual_row = None
    manual_position = None
    manual_level = None

    with st.form(
        "entrada_multiple_form",
        clear_on_submit=False,
    ):
        product_input = st.text_input(
            "Producto",
            value=product,
            disabled=bool(product_info),
            placeholder="Nombre del producto",
        )

        lot = st.text_input(
            "Lote",
            placeholder="22-10",
        )

        prod_date = st.date_input(
            "Fecha de producción",
            value=date.today(),
        )

        bundles = st.number_input(
            "Bultos por tarima",
            min_value=0,
            step=1,
        )

        pallet_qty = st.number_input(
            "Cantidad de tarimas que ingresan",
            min_value=1,
            max_value=200,
            value=1,
            step=1,
        )

        allow_level3 = st.checkbox(
            "Autorizar sobrealmacenamiento en Nivel 3",
            value=False,
            help=(
                "Nivel 3 no forma parte de la asignación normal. "
                "Solo se utilizará si ya no quedan ubicaciones N1/N2 "
                "compatibles en la zona."
            ),
        )

        if assign_mode == "Manual":
            manual_rows = (
                compatible_rows_for_sku(
                    df,
                    zone_in,
                    sku,
                )
                if sku
                else sorted(
                    df[df["zone"] == zone_in]["row_id"].unique(),
                    key=row_sort_key,
                )
            )

            manual_row = st.selectbox(
                "Fila",
                manual_rows,
                key="manual_row_in",
            )

            row_slots = df[
                (df["zone"] == zone_in)
                & (df["row_id"] == manual_row)
            ]

            positions = (
                row_slots[
                    [
                        "position",
                        "depth",
                    ]
                ]
                .drop_duplicates()
                .sort_values("depth")
            )

            manual_position = st.selectbox(
                "Posición",
                positions["position"].tolist(),
                key="manual_position_in",
            )

            normal_levels = [
                level
                for level in [1, 2]
                if can_place_on_level(
                    df,
                    zone_in,
                    manual_position,
                    level,
                )
            ]

            if normal_levels:
                valid_levels = normal_levels
            elif allow_level3 and can_place_on_level(
                df,
                zone_in,
                manual_position,
                3,
            ):
                valid_levels = [3]
            else:
                valid_levels = []

            if valid_levels:
                manual_level = st.selectbox(
                    "Nivel",
                    valid_levels,
                    key="manual_level_in",
                )
            else:
                st.warning(
                    "La posición seleccionada no tiene un nivel permitido disponible."
                )

            st.caption(
                "En modo Manual se registra una tarima por operación."
            )

        generate_plan = st.form_submit_button(
            "Generar propuesta de ubicaciones"
        )

    if generate_plan:
        final_product = (
            product
            if product_info
            else str(product_input).strip()
        )

        errors = []

        if not sku:
            errors.append(
                "Debe indicar SKU."
            )

        if not lot.strip():
            errors.append(
                "Debe indicar lote."
            )

        if not final_product:
            errors.append(
                "Debe indicar nombre del producto."
            )

        if (
            assign_mode == "Manual"
            and int(pallet_qty) != 1
        ):
            errors.append(
                "En modo Manual la cantidad debe ser 1. "
                "Use PEPS automático por filas para ingresos múltiples."
            )

        if errors:
            for message in errors:
                st.error(message)

            st.session_state.pop(
                "entry_batch_plan",
                None,
            )

        else:
            if not product_info:
                catalog = upsert_product(
                    catalog,
                    sku,
                    final_product,
                )

            if assign_mode == "PEPS automático por filas":
                proposal = plan_batch_entry_across_rows(
                    df,
                    zone_in,
                    sku,
                    int(pallet_qty),
                    allow_level3=allow_level3,
                )

            else:
                if (
                    manual_row is None
                    or manual_level is None
                    or not row_accepts_sku(
                        df,
                        zone_in,
                        manual_row,
                        sku,
                    )
                ):
                    proposal = pd.DataFrame()
                else:
                    manual_slot = df[
                        (df["zone"] == zone_in)
                        & (df["row_id"] == manual_row)
                        & (df["position"] == manual_position)
                        & (df["level"] == int(manual_level))
                    ].iloc[0]

                    proposal = pd.DataFrame(
                        [
                            {
                                "Tarima": 1,
                                "Zona": zone_in,
                                "Fila": manual_row,
                                "Posición": manual_position,
                                "Profundidad": int(manual_slot["depth"]),
                                "Nivel": int(manual_level),
                                "Tipo de ubicación": (
                                    "Sobrealmacenamiento N3"
                                    if int(manual_level) == 3
                                    else "Manual"
                                ),
                            }
                        ]
                    )

            if len(proposal) != int(pallet_qty):
                st.error(
                    f"Se encontraron {len(proposal)} ubicación(es) válidas "
                    f"para un ingreso de {int(pallet_qty)} tarima(s). "
                    "Si la capacidad N1/N2 está agotada, puede autorizar N3 "
                    "solo si realmente existe sobrealmacenamiento."
                )

                st.session_state.pop(
                    "entry_batch_plan",
                    None,
                )

            else:
                st.session_state[
                    "entry_batch_plan"
                ] = {
                    "proposal": proposal.to_dict("records"),
                    "turn": turn_in,
                    "zone": zone_in,
                    "sku": sku,
                    "product": final_product,
                    "lot": lot.strip(),
                    "production_date": prod_date.isoformat(),
                    "bundles": int(bundles),
                    "quantity": int(pallet_qty),
                    "mode": assign_mode,
                    "allow_level3": bool(allow_level3),
                }

    batch_plan = st.session_state.get(
        "entry_batch_plan"
    )

    if batch_plan:
        proposal_df = pd.DataFrame(
            batch_plan["proposal"]
        )

        st.markdown(
            "#### Propuesta automática de ubicaciones"
        )

        st.write(
            f"**{batch_plan['quantity']} tarima(s)** · "
            f"SKU **{batch_plan['sku']}** · "
            f"Lote **{batch_plan['lot']}**"
        )

        st.dataframe(
            proposal_df,
            use_container_width=True,
            hide_index=True,
        )

        row_summary = (
            proposal_df.groupby(
                ["Fila", "Nivel"]
            )
            .size()
            .reset_index(
                name="Tarimas"
            )
        )

        st.markdown(
            "##### Distribución por fila"
        )

        st.dataframe(
            row_summary,
            use_container_width=True,
            hide_index=True,
        )

        if proposal_df["Nivel"].eq(3).any():
            st.warning(
                "La propuesta utiliza Nivel 3 únicamente como "
                "sobrealmacenamiento autorizado."
            )
        else:
            st.success(
                "La propuesta utiliza únicamente N1 y N2."
            )

        confirm_batch_entry = st.checkbox(
            "Confirmo estas ubicaciones",
            key="confirm_batch_entry",
        )

        c_entry, c_cancel = st.columns(2)

        with c_entry:
            if st.button(
                f"Registrar {batch_plan['quantity']} tarima(s)",
                type="primary",
                disabled=not confirm_batch_entry,
                key="register_batch_entry",
            ):
                successful = 0

                for planned in batch_plan["proposal"]:
                    slot = df[
                        (df["zone"] == planned["Zona"])
                        & (df["row_id"] == planned["Fila"])
                        & (df["position"] == planned["Posición"])
                        & (df["level"] == int(planned["Nivel"]))
                    ]

                    if slot.empty:
                        continue

                    idx = slot.index[0]

                    if df.at[idx, "status"] != "Disponible":
                        continue

                    occupy_slot(
                        df,
                        idx,
                        batch_plan["sku"],
                        batch_plan["product"],
                        batch_plan["lot"],
                        batch_plan["production_date"],
                        batch_plan["turn"],
                        batch_plan["bundles"],
                    )

                    log_move(
                        shift=batch_plan["turn"],
                        movement_type=(
                            "Entrada múltiple PEPS"
                            if batch_plan["mode"] == "PEPS automático por filas"
                            else "Entrada"
                        ),
                        destination=(
                            f'{planned["Posición"]}-N{planned["Nivel"]}'
                        ),
                        zone_destination=planned["Zona"],
                        row_destination=planned["Fila"],
                        sku=batch_plan["sku"],
                        product=batch_plan["product"],
                        lot=batch_plan["lot"],
                        production_date=batch_plan["production_date"],
                        bundles=batch_plan["bundles"],
                        notes=(
                            f"Ingreso múltiple de {batch_plan['quantity']} tarima(s). "
                            f"Tarima {planned['Tarima']} de {batch_plan['quantity']}. "
                            f"{planned['Tipo de ubicación']}."
                        ),
                    )

                    successful += 1

                save_state(df)

                st.session_state.pop(
                    "entry_batch_plan",
                    None,
                )

                st.success(
                    f"Se registraron {successful} tarima(s) "
                    f"del lote {batch_plan['lot']}."
                )

                st.rerun()

        with c_cancel:
            if st.button(
                "Cancelar propuesta",
                key="cancel_batch_entry",
            ):
                st.session_state.pop(
                    "entry_batch_plan",
                    None,
                )
                st.rerun()

# ============================================================
# SALIDA MÚLTIPLE
# ============================================================

with tab_out:
    turn_out = st.selectbox(
        "Turno",
        TURNOS,
        key="turn_out",
    )

    occupied = df[
        df["status"] == "Ocupada"
    ].copy()

    if occupied.empty:
        st.info(
            "No hay tarimas almacenadas."
        )

    else:
        # ----------------------------------------------------
        # Seleccionar producto / SKU
        # ----------------------------------------------------
        sku_inventory = (
            occupied.groupby(
                [
                    "sku",
                    "product",
                ],
                dropna=False,
            )
            .size()
            .reset_index(
                name="tarimas"
            )
            .sort_values(
                [
                    "product",
                    "sku",
                ]
            )
        )

        sku_options = (
            sku_inventory[
                "sku"
            ]
            .astype(str)
            .tolist()
        )

        selected_out_sku = st.selectbox(
            "Producto a despachar",
            sku_options,
            format_func=lambda sku: (
                f"{sku} — "
                f"{sku_inventory.loc[sku_inventory['sku'].astype(str) == str(sku), 'product'].iloc[0]} "
                f"({int(sku_inventory.loc[sku_inventory['sku'].astype(str) == str(sku), 'tarimas'].iloc[0])} tarima(s))"
            ),
            key="selected_out_sku",
        )

        product_stock = occupied[
            occupied[
                "sku"
            ].astype(str)
            == str(
                selected_out_sku
            )
        ].copy()

        available_pallets = len(
            product_stock
        )

        st.success(
            f"Inventario disponible del SKU {selected_out_sku}: "
            f"**{available_pallets} tarima(s)**."
        )

        requested_qty = st.number_input(
            "Cantidad de tarimas del pedido",
            min_value=1,
            max_value=max(
                available_pallets,
                1,
            ),
            value=min(
                1,
                max(
                    available_pallets,
                    1,
                ),
            ),
            step=1,
            key="requested_out_qty",
        )

        selection_mode = st.radio(
            "Forma de selección",
            [
                "PEPS automático",
                "Selección manual",
            ],
            horizontal=True,
            key="out_selection_mode",
        )

        # ----------------------------------------------------
        # Calcular bloqueos de cada tarima disponible
        # ----------------------------------------------------
        product_stock[
            "parsed_date"
        ] = pd.to_datetime(
            product_stock[
                "production_date"
            ],
            errors="coerce",
        )

        product_stock[
            "tarimas_delante"
        ] = product_stock.apply(
            lambda r: front_pallets_count(
                df,
                r["zone"],
                r["row_id"],
                int(
                    r["depth"]
                ),
            ),
            axis=1,
        )

        product_stock[
            "tarimas_encima"
        ] = product_stock.apply(
            lambda r: count_above(
                df,
                r["zone"],
                r["position"],
                int(
                    r["level"]
                ),
            ),
            axis=1,
        )

        product_stock[
            "bloqueos_totales"
        ] = (
            product_stock[
                "tarimas_delante"
            ]
            + product_stock[
                "tarimas_encima"
            ]
        )

        # ----------------------------------------------------
        # Modo automático: fecha más antigua primero.
        # Para fechas iguales, prioriza menor bloqueo.
        # ----------------------------------------------------
        if (
            selection_mode
            == "PEPS automático"
        ):
            automatic_stock = (
                product_stock
                .assign(
                    date_missing=product_stock[
                        "parsed_date"
                    ].isna()
                )
                .sort_values(
                    [
                        "date_missing",
                        "parsed_date",
                        "bloqueos_totales",
                        "zone",
                        "row_id",
                        "depth",
                        "level",
                    ],
                    ascending=[
                        True,
                        True,
                        True,
                        True,
                        True,
                        True,
                        False,
                    ],
                )
            )

            selected_rows = (
                automatic_stock
                .head(
                    int(
                        requested_qty
                    )
                )
                .copy()
            )

            st.info(
                "PEPS automático selecciona primero las tarimas "
                "con fecha de producción más antigua. "
                "Si hay empate, prioriza la de menor bloqueo."
            )

        # ----------------------------------------------------
        # Modo manual: usuario elige las tarimas exactas.
        # ----------------------------------------------------
        else:
            label_to_index = {}

            manual_options = []

            manual_sorted = (
                product_stock
                .sort_values(
                    [
                        "production_date",
                        "zone",
                        "row_id",
                        "depth",
                        "level",
                    ]
                )
            )

            for idx, row in (
                manual_sorted
                .iterrows()
            ):
                label = (
                    f'{row["position"]}-N{row["level"]} | '
                    f'Lote {row["lot"]} | '
                    f'Fecha {row["production_date"] or "Sin fecha"} | '
                    f'{row["zone"]} / {row["row_id"]} | '
                    f'Bloqueos {int(row["bloqueos_totales"])}'
                )

                manual_options.append(
                    label
                )

                label_to_index[
                    label
                ] = idx

            selected_manual_labels = (
                st.multiselect(
                    "Seleccione las tarimas exactas",
                    manual_options,
                    max_selections=int(
                        requested_qty
                    ),
                    key="manual_out_pallets",
                )
            )

            selected_indices = [
                label_to_index[
                    label
                ]
                for label
                in selected_manual_labels
            ]

            selected_rows = (
                product_stock.loc[
                    selected_indices
                ]
                .copy()
                if selected_indices
                else product_stock.iloc[
                    0:0
                ].copy()
            )

            if (
                len(
                    selected_rows
                )
                < int(
                    requested_qty
                )
            ):
                st.warning(
                    f"Seleccione exactamente {int(requested_qty)} tarima(s). "
                    f"Actualmente ha seleccionado {len(selected_rows)}."
                )

        # ----------------------------------------------------
        # Vista previa del pedido
        # ----------------------------------------------------
        if not selected_rows.empty:
            st.markdown(
                "#### Tarimas seleccionadas para el pedido"
            )

            preview = (
                selected_rows[
                    [
                        "position",
                        "level",
                        "lot",
                        "production_date",
                        "zone",
                        "row_id",
                        "bundles",
                        "tarimas_delante",
                        "tarimas_encima",
                        "bloqueos_totales",
                    ]
                ]
                .copy()
            )

            preview = preview.rename(
                columns={
                    "position": "Posición",
                    "level": "Nivel",
                    "lot": "Lote",
                    "production_date": "Fecha producción",
                    "zone": "Zona",
                    "row_id": "Fila",
                    "bundles": "Bultos",
                    "tarimas_delante": "Tarimas delante",
                    "tarimas_encima": "Tarimas encima",
                    "bloqueos_totales": "Bloqueos",
                }
            )

            st.dataframe(
                preview,
                use_container_width=True,
                hide_index=True,
            )

            total_bundles = int(
                pd.to_numeric(
                    selected_rows[
                        "bundles"
                    ],
                    errors="coerce",
                )
                .fillna(0)
                .sum()
            )

            blocked_selected = int(
                (
                    selected_rows[
                        "bloqueos_totales"
                    ]
                    > 0
                ).sum()
            )

            q1, q2, q3 = st.columns(
                3
            )

            q1.metric(
                "Tarimas del pedido",
                len(
                    selected_rows
                ),
            )

            q2.metric(
                "Bultos del pedido",
                total_bundles,
            )

            q3.metric(
                "Tarimas con bloqueo",
                blocked_selected,
            )

            if blocked_selected > 0:
                st.warning(
                    f"{blocked_selected} de las tarimas seleccionadas "
                    "presentan una o más tarimas delante o encima. "
                    "Los bloqueos deben resolverse físicamente antes del despacho."
                )
            else:
                st.success(
                    "Todas las tarimas seleccionadas aparecen accesibles."
                )

            # Para selección manual se requiere exactamente la cantidad pedida.
            correct_quantity = (
                len(
                    selected_rows
                )
                == int(
                    requested_qty
                )
            )

            confirm_batch_access = (
                st.checkbox(
                    "Confirmo que los bloqueos físicos del pedido ya fueron liberados",
                    disabled=(
                        blocked_selected
                        == 0
                    ),
                    key="confirm_batch_access",
                )
            )

            access_ready = (
                blocked_selected
                == 0
                or confirm_batch_access
            )

            confirm_dispatch = (
                st.checkbox(
                    f"Confirmo el despacho de {int(requested_qty)} tarima(s)",
                    key="confirm_batch_dispatch",
                )
            )

            if st.button(
                f"Registrar salida de {int(requested_qty)} tarima(s)",
                type="primary",
                disabled=(
                    not correct_quantity
                    or not access_ready
                    or not confirm_dispatch
                ),
                key="register_batch_out",
            ):
                # Guardar cada tarima como movimiento individual
                # para conservar trazabilidad por lote y ubicación.
                for idx, row in (
                    selected_rows
                    .iterrows()
                ):
                    log_move(
                        shift=turn_out,
                        movement_type="Salida",
                        origin=(
                            f'{row["position"]}-N{row["level"]}'
                        ),
                        zone_origin=(
                            row["zone"]
                        ),
                        row_origin=(
                            row["row_id"]
                        ),
                        sku=(
                            row["sku"]
                        ),
                        product=(
                            row["product"]
                        ),
                        lot=(
                            row["lot"]
                        ),
                        production_date=(
                            row[
                                "production_date"
                            ]
                        ),
                        bundles=(
                            row["bundles"]
                        ),
                        notes=(
                            f"Pedido múltiple de {int(requested_qty)} tarima(s). "
                            f"Bloqueos identificados antes del despacho: "
                            f"{int(row['bloqueos_totales'])}."
                        ),
                    )

                    clear_slot(
                        df,
                        idx,
                    )

                save_state(
                    df
                )

                st.success(
                    f"Salida registrada: "
                    f"{int(requested_qty)} tarima(s) del SKU "
                    f"{selected_out_sku}."
                )

                st.rerun()

        elif (
            selection_mode
            == "Selección manual"
        ):
            st.info(
                "Seleccione las tarimas que formarán parte del pedido."
            )

# ============================================================
# RELOCALIZAR — VISUAL POR TARIMA
# ============================================================

with tab_relocate:
    st.markdown(
        "### Relocalización visual de tarimas"
    )

    st.caption(
        "Seleccione las filas y mueva únicamente las tarimas que necesite. "
        "Cada tarjeta representa una sola tarima."
    )

    turn_move = st.selectbox(
        "Turno",
        TURNOS,
        key="turn_move",
    )

    relocation_zone = st.selectbox(
        "Zona de trabajo",
        list(ZONES.keys()),
        key="relocation_zone",
    )

    zone_rows = sorted(
        df[
            df["zone"] == relocation_zone
        ]["row_id"].unique(),
        key=row_sort_key,
    )

    r1, r2 = st.columns(2)

    with r1:
        origin_row_id = st.selectbox(
            "Fila origen",
            zone_rows,
            key="relocation_origin_row",
        )

    origin_inventory = df[
        (df["zone"] == relocation_zone)
        & (df["row_id"] == origin_row_id)
        & (df["status"] == "Ocupada")
    ].copy()

    if origin_inventory.empty:
        with r2:
            st.selectbox(
                "Fila destino",
                [],
                disabled=True,
                key="empty_destination_row",
            )

        st.info(
            "La fila origen no tiene tarimas."
        )

    else:
        origin_skus = [
            s
            for s in origin_inventory["sku"].astype(str).unique()
            if s
        ]

        origin_sku = (
            origin_skus[0]
            if origin_skus
            else ""
        )

        compatible_dest_rows = [
            row_id
            for row_id in zone_rows
            if (
                row_id != origin_row_id
                and row_accepts_sku(
                    df,
                    relocation_zone,
                    row_id,
                    origin_sku,
                )
            )
        ]

        with r2:
            destination_row_id = st.selectbox(
                "Fila destino",
                compatible_dest_rows,
                key="relocation_destination_row",
                disabled=not compatible_dest_rows,
            )

        if not compatible_dest_rows:
            st.warning(
                "No hay otra fila compatible disponible para este SKU."
            )

        else:
            allow_relocation_n3 = st.checkbox(
                "Autorizar Nivel 3 por sobrealmacenamiento",
                value=False,
                key="relocation_allow_n3",
            )

            direct_origin = direct_accessible_pallets_in_row(
                df,
                relocation_zone,
                origin_row_id,
            )

            total_origin = len(
                origin_inventory
            )

            direct_count = len(
                direct_origin
            )

            info1, info2, info3 = st.columns(3)

            info1.metric(
                "Tarimas en fila origen",
                total_origin,
            )

            info2.metric(
                "Tarimas movibles ahora",
                direct_count,
            )

            destination_current = int(
                (
                    (df["zone"] == relocation_zone)
                    & (df["row_id"] == destination_row_id)
                    & (df["status"] == "Ocupada")
                ).sum()
            )

            info3.metric(
                "Tarimas actuales en destino",
                destination_current,
            )

            if direct_origin.empty:
                st.warning(
                    "No hay tarimas accesibles directamente en esta fila. "
                    "Para poder mover una tarima debe estar libre por arriba "
                    "y tener acceso físico desde el frente."
                )

            else:
                relocation_mode = st.radio(
                    "¿Cómo desea moverlas?",
                    [
                        "Arrastrar tarjetas",
                        "Seleccionar varias",
                    ],
                    horizontal=True,
                    key="relocation_mode",
                )

                # ====================================================
                # MODO ARRASTRAR
                # ====================================================
                if relocation_mode == "Arrastrar tarjetas":
                    st.markdown(
                        "#### Tarimas disponibles para mover"
                    )

                    st.caption(
                        "Tome únicamente la tarjeta que quiera mover y arrástrela "
                        "al recuadro «SOLTAR AQUÍ». No se mueve la fila completa."
                    )

                    origin_items = []
                    label_to_index = {}

                    direct_sorted = direct_origin.sort_values(
                        [
                            "production_date",
                            "depth",
                            "level",
                        ],
                        ascending=[
                            True,
                            True,
                            False,
                        ],
                    )

                    for idx, row in direct_sorted.iterrows():
                        label = pallet_drag_label(
                            idx,
                            row,
                        )

                        origin_items.append(
                            label
                        )

                        label_to_index[
                            label
                        ] = idx

                    # Destination container intentionally starts empty.
                    original_containers = [
                        {
                            "header": (
                                f"TARIMAS MOVIBLES · {origin_row_id}"
                            ),
                            "items": origin_items,
                        },
                        {
                            "header": (
                                f"SOLTAR AQUÍ · {destination_row_id}"
                            ),
                            "items": [],
                        },
                    ]

                    drag_style = """
                    .sortable-component {
                        border: 1px solid #CBD5E1;
                        border-radius: 14px;
                        padding: 10px;
                        background: #F8FAFC;
                    }

                    .sortable-container {
                        margin-bottom: 14px;
                    }

                    .sortable-container-header {
                        font-weight: 800;
                        color: #0F172A;
                        font-size: 15px;
                        padding: 10px;
                    }

                    .sortable-container-body {
                        min-height: 95px;
                        background: #FFFFFF;
                        border: 2px dashed #CBD5E1;
                        border-radius: 12px;
                        padding: 10px;
                    }

                    .sortable-item {
                        cursor: grab;
                        border: 1px solid #60A5FA;
                        border-radius: 10px;
                        padding: 12px;
                        margin: 7px 0;
                        background: #EFF6FF;
                        color: #0F172A;
                        font-size: 14px;
                        font-weight: 600;
                    }

                    .sortable-item:active {
                        cursor: grabbing;
                    }
                    """

                    moved_containers = sort_items(
                        original_containers,
                        multi_containers=True,
                        custom_style=drag_style,
                    )

                    if moved_containers:
                        dropped_items = list(
                            moved_containers[1]["items"]
                        )

                        if dropped_items:
                            st.markdown(
                                "#### Movimiento preparado"
                            )

                            st.success(
                                f"Ha seleccionado {len(dropped_items)} "
                                f"tarima(s) para mover de {origin_row_id} "
                                f"a {destination_row_id}."
                            )

                            preview_rows = []

                            for label in dropped_items:
                                idx = label_to_index.get(
                                    label
                                )

                                if idx is None:
                                    continue

                                row = df.loc[
                                    idx
                                ]

                                preview_rows.append(
                                    {
                                        "Posición actual": (
                                            f'{row["position"]}-N{row["level"]}'
                                        ),
                                        "SKU": row["sku"],
                                        "Lote": row["lot"],
                                        "Fecha": row["production_date"],
                                    }
                                )

                            if preview_rows:
                                st.dataframe(
                                    pd.DataFrame(
                                        preview_rows
                                    ),
                                    use_container_width=True,
                                    hide_index=True,
                                )

                            confirm_drag = st.checkbox(
                                "Confirmo el movimiento de estas tarimas",
                                key="confirm_drag_relocation",
                            )

                            if st.button(
                                "Aplicar movimiento",
                                type="primary",
                                disabled=not confirm_drag,
                                key="apply_drag_relocation",
                            ):
                                moved_count = 0
                                failed = []

                                for label in dropped_items:
                                    origin_idx = label_to_index.get(
                                        label
                                    )

                                    if origin_idx is None:
                                        continue

                                    row = df.loc[
                                        origin_idx
                                    ].copy()

                                    if (
                                        row["status"]
                                        != "Ocupada"
                                    ):
                                        failed.append(
                                            label
                                        )
                                        continue

                                    # Check again at execution time.
                                    if not can_remove(
                                        df,
                                        relocation_zone,
                                        row["position"],
                                        int(
                                            row["level"]
                                        ),
                                    ):
                                        failed.append(
                                            label
                                        )
                                        continue

                                    dest = relocation_destination_slot(
                                        df,
                                        relocation_zone,
                                        destination_row_id,
                                        row["sku"],
                                        allow_level3=allow_relocation_n3,
                                    )

                                    if dest is None:
                                        failed.append(
                                            label
                                        )
                                        continue

                                    dest_idx = dest.name

                                    occupy_slot(
                                        df,
                                        dest_idx,
                                        row["sku"],
                                        row["product"],
                                        row["lot"],
                                        row["production_date"],
                                        row["entry_shift"],
                                        int(
                                            row["bundles"]
                                        ),
                                    )

                                    clear_slot(
                                        df,
                                        origin_idx,
                                    )

                                    log_move(
                                        shift=turn_move,
                                        movement_type=(
                                            "Relocalización visual"
                                        ),
                                        origin=(
                                            f'{row["position"]}'
                                            f'-N{row["level"]}'
                                        ),
                                        destination=(
                                            f'{dest["position"]}'
                                            f'-N{dest["level"]}'
                                        ),
                                        zone_origin=relocation_zone,
                                        zone_destination=relocation_zone,
                                        row_origin=origin_row_id,
                                        row_destination=destination_row_id,
                                        sku=row["sku"],
                                        product=row["product"],
                                        lot=row["lot"],
                                        production_date=(
                                            row["production_date"]
                                        ),
                                        bundles=row["bundles"],
                                        notes=(
                                            "Tarima movida mediante "
                                            "interfaz visual de arrastre."
                                        ),
                                    )

                                    moved_count += 1

                                save_state(
                                    df
                                )

                                if moved_count:
                                    st.success(
                                        f"{moved_count} tarima(s) "
                                        "relocalizada(s). Inventario e "
                                        "historial actualizados."
                                    )

                                if failed:
                                    st.warning(
                                        f"{len(failed)} tarima(s) no pudieron "
                                        "moverse porque dejaron de estar "
                                        "accesibles o no hubo espacio válido."
                                    )

                                st.rerun()

                # ====================================================
                # MODO SELECCIÓN MÚLTIPLE
                # ====================================================
                else:
                    st.markdown(
                        "#### Selección rápida"
                    )

                    label_to_index = {}

                    selectable = []

                    for idx, row in direct_origin.iterrows():
                        label = pallet_drag_label(
                            idx,
                            row,
                        )

                        selectable.append(
                            label
                        )

                        label_to_index[
                            label
                        ] = idx

                    selected_labels = st.multiselect(
                        "Marque únicamente las tarimas que desea mover",
                        selectable,
                        key="relocation_multi_select",
                    )

                    st.caption(
                        "Puede seleccionar una sola tarima o varias. "
                        "No se mueve el resto de la fila."
                    )

                    if selected_labels:
                        st.info(
                            f"{len(selected_labels)} tarima(s) seleccionada(s)."
                        )

                    confirm_multi = st.checkbox(
                        "Confirmo las tarimas seleccionadas",
                        key="confirm_multi_relocation",
                        disabled=not selected_labels,
                    )

                    if st.button(
                        "Relocalizar seleccionadas",
                        type="primary",
                        disabled=(
                            not selected_labels
                            or not confirm_multi
                        ),
                        key="relocate_selected_pallets",
                    ):
                        moved = 0
                        failed = []

                        for label in selected_labels:
                            origin_idx = label_to_index[
                                label
                            ]

                            row = df.loc[
                                origin_idx
                            ].copy()

                            if (
                                row["status"]
                                != "Ocupada"
                            ):
                                failed.append(
                                    label
                                )
                                continue

                            if not can_remove(
                                df,
                                relocation_zone,
                                row["position"],
                                int(
                                    row["level"]
                                ),
                            ):
                                failed.append(
                                    label
                                )
                                continue

                            dest = relocation_destination_slot(
                                df,
                                relocation_zone,
                                destination_row_id,
                                row["sku"],
                                allow_level3=allow_relocation_n3,
                            )

                            if dest is None:
                                failed.append(
                                    label
                                )
                                continue

                            dest_idx = dest.name

                            occupy_slot(
                                df,
                                dest_idx,
                                row["sku"],
                                row["product"],
                                row["lot"],
                                row["production_date"],
                                row["entry_shift"],
                                int(
                                    row["bundles"]
                                ),
                            )

                            clear_slot(
                                df,
                                origin_idx,
                            )

                            log_move(
                                shift=turn_move,
                                movement_type=(
                                    "Relocalización visual"
                                ),
                                origin=(
                                    f'{row["position"]}-N{row["level"]}'
                                ),
                                destination=(
                                    f'{dest["position"]}-N{dest["level"]}'
                                ),
                                zone_origin=relocation_zone,
                                zone_destination=relocation_zone,
                                row_origin=origin_row_id,
                                row_destination=destination_row_id,
                                sku=row["sku"],
                                product=row["product"],
                                lot=row["lot"],
                                production_date=(
                                    row["production_date"]
                                ),
                                bundles=row["bundles"],
                                notes=(
                                    "Tarima seleccionada visualmente "
                                    "para relocalización."
                                ),
                            )

                            moved += 1

                        save_state(
                            df
                        )

                        if moved:
                            st.success(
                                f"{moved} tarima(s) relocalizada(s)."
                            )

                        if failed:
                            st.warning(
                                f"{len(failed)} tarima(s) no pudieron moverse."
                            )

                        st.rerun()

# ============================================================
# REACOMODO PEPS
# ============================================================

with tab_peps:
    st.markdown(
        "Este módulo revisa una fila y muestra cómo debería ordenarse "
        "el SKU desde el acceso hacia el fondo: **antiguo → nuevo**."
    )

    peps_zone = st.selectbox(
        "Zona",
        list(ZONES.keys()),
        key="peps_zone",
    )

    peps_rows = sorted(
        df[df["zone"] == peps_zone]["row_id"].unique()
    )

    peps_row = st.selectbox(
        "Fila",
        peps_rows,
        key="peps_row",
    )

    row_inventory = df[
        (df["zone"] == peps_zone)
        & (df["row_id"] == peps_row)
        & (df["status"] == "Ocupada")
    ]

    sku_options = sorted(
        [
            sku
            for sku in row_inventory["sku"].unique()
            if sku
        ]
    )

    if not sku_options:
        st.info("La fila seleccionada no tiene SKU registrados.")
    else:
        peps_sku = st.selectbox(
            "SKU a revisar",
            sku_options,
            key="peps_sku",
        )

        current = peps_sequence_for_sku(
            df,
            peps_zone,
            peps_row,
            peps_sku,
        )

        ordered = peps_is_ordered(
            df,
            peps_zone,
            peps_row,
            peps_sku,
        )

        st.markdown("#### Orden actual desde el acceso → fondo")

        current_view = current[
            [
                "position",
                "depth",
                "level",
                "lot",
                "production_date",
            ]
        ].copy()

        st.dataframe(
            current_view,
            use_container_width=True,
            hide_index=True,
        )

        if ordered:
            st.success("La secuencia del SKU cumple el criterio PEPS.")
        else:
            st.warning("La secuencia del SKU no está ordenada por PEPS.")

            recommendation = recommended_peps_table(
                df,
                peps_zone,
                peps_row,
                peps_sku,
            )

            st.markdown("#### Orden recomendado")

            st.dataframe(
                recommendation[
                    [
                        "position",
                        "depth",
                        "level",
                        "lot",
                        "production_date",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

            # Estimación sencilla de reubicaciones:
            current_lots = current["lot"].tolist()
            recommended_lots = recommendation["lot"].tolist()

            mismatches = sum(
                a != b
                for a, b in zip(
                    current_lots,
                    recommended_lots,
                )
            )

            estimated_moves = mismatches * 2

            st.info(
                f"Estimación preliminar: {mismatches} ubicación(es) "
                f"deben cambiar. Aproximadamente {estimated_moves} "
                "movimientos de manipulación considerando retiro y nueva colocación."
            )

            st.caption(
                "La herramienta propone el orden; la relocalización física se registra "
                "desde la pestaña «Relocalizar» para mantener trazabilidad."
            )

# ============================================================
# CONSULTA GLOBAL
# ============================================================

st.divider()
st.subheader("Consulta global")

query = st.text_input(
    "Buscar en toda la bodega",
    placeholder="SKU, lote o producto",
    key="global_query",
).strip()

if query:
    result = df[
        df.apply(
            lambda r: query.lower()
            in f'{r["sku"]} {r["lot"]} {r["product"]}'.lower(),
            axis=1,
        )
    ].copy()

    if result.empty:
        st.warning("No se encontraron resultados.")
    else:
        result["tarimas_delante"] = result.apply(
            lambda r: front_pallets_count(
                df,
                r["zone"],
                r["row_id"],
                int(r["depth"]),
            ),
            axis=1,
        )

        result["tarimas_encima"] = result.apply(
            lambda r: count_above(
                df,
                r["zone"],
                r["position"],
                int(r["level"]),
            ),
            axis=1,
        )

        st.dataframe(
            result[
                [
                    "zone",
                    "row_id",
                    "position",
                    "depth",
                    "level",
                    "sku",
                    "product",
                    "lot",
                    "production_date",
                    "entry_shift",
                    "bundles",
                    "tarimas_delante",
                    "tarimas_encima",
                ]
            ].sort_values(
                [
                    "production_date",
                    "zone",
                    "row_id",
                    "depth",
                    "level",
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )

# ============================================================
# HISTORIAL
# ============================================================

st.divider()
st.subheader("Historial de movimientos")

moves = load_moves()

if moves.empty:
    st.info("No hay movimientos registrados.")
else:
    f1, f2 = st.columns(2)

    with f1:
        shift_filter = st.selectbox(
            "Filtrar por turno",
            ["Todos"] + TURNOS,
        )

    with f2:
        type_options = [
            "Todos",
            "Entrada",
            "Entrada PEPS",
            "Salida",
            "Relocalización",
        ]

        move_filter = st.selectbox(
            "Filtrar por movimiento",
            type_options,
        )

    filtered = moves.copy()

    if shift_filter != "Todos":
        filtered = filtered[
            filtered["shift"] == shift_filter
        ]

    if move_filter != "Todos":
        filtered = filtered[
            filtered["movement_type"] == move_filter
        ]

    history_view = (
        filtered
        .tail(300)
        .iloc[::-1]
        .copy()
    )

    history_view.insert(
        0,
        "registro_id",
        history_view.index.astype(int),
    )

    st.dataframe(
        history_view,
        use_container_width=True,
        hide_index=True,
    )

    excel_history = history_excel_bytes(
        moves,
        df,
    )

    st.download_button(
        "Descargar historial en Excel",
        data=excel_history,
        file_name=(
            "Historial_Movimientos_COONAPROSAL.xlsx"
        ),
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )

    st.markdown("#### Corregir una línea del historial")

    st.caption(
        "Seleccione únicamente el movimiento incorrecto. "
        "Puede borrar solo la línea o, si fue una entrada equivocada, "
        "anular también la tarima creada en el inventario."
    )

    record_options = (
        history_view[
            "registro_id"
        ]
        .astype(int)
        .tolist()
    )

    if record_options:
        record_id = st.selectbox(
            "Registro a corregir",
            record_options,
            format_func=lambda idx: (
                f"Registro {idx} | "
                f"{moves.loc[idx, 'timestamp']} | "
                f"{moves.loc[idx, 'movement_type']} | "
                f"SKU {moves.loc[idx, 'sku']} | "
                f"Lote {moves.loc[idx, 'lot']} | "
                f"{moves.loc[idx, 'destination'] or moves.loc[idx, 'origin']}"
            ),
            key="single_history_record",
        )

        selected_move = moves.loc[
            record_id
        ]

        st.info(
            f"Seleccionado: {selected_move['movement_type']} · "
            f"SKU {selected_move['sku']} · "
            f"Lote {selected_move['lot']} · "
            f"Destino {selected_move['destination'] or '—'}"
        )

        confirm_single = st.checkbox(
            "Confirmo que este es el registro que deseo corregir",
            key="confirm_single_history",
        )

        delete_col, undo_col = st.columns(2)

        with delete_col:
            if st.button(
                "Borrar solo esta línea",
                disabled=not confirm_single,
                key="delete_history_line",
            ):
                updated_moves = (
                    moves
                    .drop(
                        index=record_id
                    )
                    .reset_index(
                        drop=True
                    )
                )

                save_moves(
                    updated_moves
                )

                st.success(
                    "Se eliminó únicamente esa línea del historial. "
                    "El inventario no cambió."
                )

                st.rerun()

        with undo_col:
            is_entry = (
                "Entrada"
                in str(
                    selected_move[
                        "movement_type"
                    ]
                )
            )

            if st.button(
                "Anular entrada y quitar tarima",
                disabled=(
                    not confirm_single
                    or not is_entry
                    or not str(
                        selected_move[
                            "destination"
                        ]
                    ).strip()
                ),
                key="undo_history_entry",
            ):
                destination = str(
                    selected_move[
                        "destination"
                    ]
                ).strip()

                if "-N" not in destination:
                    st.error(
                        "No se pudo interpretar la ubicación de esta entrada."
                    )
                else:
                    dest_position = (
                        destination
                        .split("-N")[0]
                    )

                    dest_level = int(
                        destination
                        .split("-N")[1]
                    )

                    state_match = df[
                        (
                            df["position"]
                            == dest_position
                        )
                        & (
                            df["level"]
                            == dest_level
                        )
                        & (
                            df["status"]
                            == "Ocupada"
                        )
                        & (
                            df["sku"]
                            .astype(str)
                            == str(
                                selected_move[
                                    "sku"
                                ]
                            )
                        )
                        & (
                            df["lot"]
                            .astype(str)
                            == str(
                                selected_move[
                                    "lot"
                                ]
                            )
                        )
                    ]

                    if state_match.empty:
                        st.error(
                            "La tarima asociada ya no está en esa ubicación. "
                            "Puede borrar solo la línea del historial, "
                            "pero no se puede revertir automáticamente el inventario."
                        )
                    else:
                        state_idx = (
                            state_match.index[0]
                        )

                        # Seguridad: solo se anula si no hay una tarima encima.
                        if not can_remove(
                            df,
                            state_match.iloc[0]["zone"],
                            dest_position,
                            dest_level,
                        ):
                            st.error(
                                "No se puede anular automáticamente porque "
                                "existe una tarima encima. Relocalícela primero."
                            )
                        else:
                            clear_slot(
                                df,
                                state_idx,
                            )

                            save_state(
                                df
                            )

                            updated_moves = (
                                moves
                                .drop(
                                    index=record_id
                                )
                                .reset_index(
                                    drop=True
                                )
                            )

                            save_moves(
                                updated_moves
                            )

                            st.success(
                                "Entrada anulada: se eliminó la línea del historial "
                                "y también la tarima asociada del inventario."
                            )

                            st.rerun()

# ============================================================
# CATÁLOGO DE PRODUCTOS
# ============================================================

st.divider()
st.subheader("Catálogo SKU → Producto")

st.caption(
    "Este catálogo permite que al digitar un código SKU durante una entrada, "
    "la herramienta complete automáticamente el nombre del producto."
)

catalog_editor = st.data_editor(
    catalog,
    use_container_width=True,
    hide_index=True,
    num_rows="dynamic",
    key="catalog_editor",
)

if st.button(
    "Guardar catálogo de productos",
    key="save_catalog_button",
):
    save_catalog(
        pd.DataFrame(
            catalog_editor
        )
    )

    st.success(
        "Catálogo actualizado."
    )

    st.rerun()


# ============================================================
# ADMINISTRACIÓN
# ============================================================

st.divider()
st.subheader("Administración")

a1, a2 = st.columns(2)

with a1:
    st.markdown("#### Borrar solo historial")

    st.caption(
        "Conserva el inventario y las ubicaciones actuales."
    )

    confirm_history = st.checkbox(
        "Confirmo que deseo borrar el historial",
        key="confirm_history",
    )

    if st.button(
        "Borrar historial",
        disabled=not confirm_history,
    ):
        save_moves(pd.DataFrame(columns=MOVE_COLUMNS))
        st.success("Historial borrado.")
        st.rerun()

with a2:
    st.markdown("#### Reiniciar almacén completo")

    st.caption(
        "Borra inventario, ubicaciones y movimientos."
    )

    confirm_reset = st.checkbox(
        "Confirmo que deseo reiniciar todo",
        key="confirm_reset",
    )

    if st.button(
        "Reiniciar todo",
        disabled=not confirm_reset,
    ):
        save_state(create_empty_state())
        save_moves(pd.DataFrame(columns=MOVE_COLUMNS))
        st.success("Almacén reiniciado.")
        st.rerun()
