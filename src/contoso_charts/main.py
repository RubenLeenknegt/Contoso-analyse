from contoso_charts.cfo_charts import (
    card_margin,
    card_total_cost,
    card_total_profit,
    card_total_sales,
    revenue_year_over_year,
    sales_margin_per_country,
    exchange_rate_volatility,
    exchange_rate_vs_sales,
)

from contoso_charts.marketing_manager_charts import (
    card_total_returns,
    card_active_promotions,
    card_total_discount,
    sales_with_promotion,
    best_selling_campaign,
    sales_per_channel_and_region,
    sales_per_category,
    discount_per_currency,
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
            file.write(
                fig.to_html(full_html=False, include_plotlyjs="cdn", config={"responsive": True})
            )
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
    marketing_figures = [
        (card_total_sales(model), "24%"),
        (card_total_returns(model), "24%"),
        (card_active_promotions(model), "24%"),
        (card_total_discount(model), "24%"),
        (sales_with_promotion(model), "49%"),
        (best_selling_campaign(model), "49%"),
        (sales_per_channel_and_region(model), "98%"),
        (sales_per_category(model), "49%"),
        (discount_per_currency(model), "49%"),
    ]

    OUTPUT_DIR.mkdir(exist_ok=True)
    save_page("cfo.html", "chief financial officer (CFO)", cfo_figures)
    save_page("marketing.html", "Marketing manager", marketing_figures)


if __name__ == "__main__":
    main()
