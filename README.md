# Contoso charts

Generates Plotly dashboards (CFO and Marketing manager) from the Contoso CSV data.

## Requirements

- [uv](https://docs.astral.sh/uv/)
- Python 3.14 (uv installs it automatically if it is missing)

## Data

The CSV files must be in the `data/` folder at the project root:

```
data/
├── Dim_Calendar.csv
├── Dim_Channel.csv
├── Dim_Currency.csv
├── Dim_Geography.csv
├── Dim_Product.csv
├── Dim_Product_Category.csv
├── Dim_Product_Subcategory.csv
├── Dim_Promotion.csv
├── Dim_Stores.csv
├── Fact_ExchangeRate.csv
└── Fact_Sales.csv
```

## Run

```sh
uv sync
uv run contoso-charts
```

This writes two pages to `output/`:

- `output/cfo.html`
- `output/marketing.html`

Open them in a browser. An internet connection is needed to view them, because Plotly is loaded from a CDN.
