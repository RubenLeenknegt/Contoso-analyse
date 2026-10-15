from contoso_charts.charts import (
    card_margin,
    card_total_cost,
    card_total_profit,
    card_total_sales,
    revenue_year_over_year,
    sales_margin_per_country,
    exchange_rate_volatility,
    exchange_rate_vs_sales
)
from contoso_charts.config import OUTPUT_DIR
from contoso_charts.data import load_model

def save_page(file_name, title, figures):
    """Write a heading and all figures into one HTML file, side by side where they fit."""
    path = OUTPUT_DIR / file_name
    with open(path, "w", encoding="utf-8") as file:
        file.write(f"<h1>{title}</h1>")
        for fig, width in figures:
            file.write(f'<div style="display: inline-block; vertical-align: top; width: {width};">')
            file.write(fig.to_html(full_html=False, include_plotlyjs="cdn",
                                   config={"responsive": True}))
            file.write("</div>")


def main() -> None:
    model = load_model()

    cfo_figures = [
        (card_total_sales(model), "24%"),
        (card_total_cost(model), "24%"),
        (card_total_profit(model), "24%"),
        (card_margin(model), "24%"),
        (revenue_year_over_year(model), "49%"),
        (sales_margin_per_country(model), "49%"),
        (exchange_rate_vs_sales(model), "49%"),
        (exchange_rate_volatility(model), "49%"),
    ]
    marketing_figures = []

    OUTPUT_DIR.mkdir(exist_ok=True)
    save_page("cfo.html", "chief financial officer (CFO)", cfo_figures)
    save_page("marketing.html", "Marketing manager", marketing_figures)


if __name__ == "__main__":
    main()