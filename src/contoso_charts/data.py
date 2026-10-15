from dataclasses import dataclass

import pandas as pd

from contoso_charts.config import DATA_DIR


@dataclass(frozen=True)
class Model:
    """All tables of the Contoso star schema, one DataFrame per CSV."""

    sales: pd.DataFrame
    exchange_rate: pd.DataFrame
    calendar: pd.DataFrame
    channel: pd.DataFrame
    currency: pd.DataFrame
    geography: pd.DataFrame
    product: pd.DataFrame
    product_category: pd.DataFrame
    product_subcategory: pd.DataFrame
    promotion: pd.DataFrame
    stores: pd.DataFrame


DATE_FORMAT = "%Y-%m-%d %H:%M:%S,%f"


def _read_table(file_name: str, date_columns: list[str] | None = None) -> pd.DataFrame:
    """Read one CSV from the data folder with Dutch decimals and parsed dates."""
    return pd.read_csv(
        DATA_DIR / file_name,
        encoding="utf-8-sig",
        decimal=",",
        parse_dates=date_columns,
        date_format=DATE_FORMAT,
    )


def load_model() -> Model:
    """Load every CSV once and return them bundled in a Model."""
    return Model(
        sales=_read_table("Fact_Sales.csv", date_columns=["DateKey"]),
        exchange_rate=_read_table("Fact_ExchangeRate.csv", date_columns=["YearMonth"]),
        calendar=_read_table("Dim_Calendar.csv", date_columns=["Date"]),
        channel=_read_table("Dim_Channel.csv"),
        currency=_read_table("Dim_Currency.csv"),
        geography=_read_table("Dim_Geography.csv"),
        product=_read_table("Dim_Product.csv"),
        product_category=_read_table("Dim_Product_Category.csv"),
        product_subcategory=_read_table("Dim_Product_Subcategory.csv"),
        promotion=_read_table("Dim_Promotion.csv", date_columns=["StartDate", "EndDate"]),
        stores=_read_table("Dim_Stores.csv"),
    )
