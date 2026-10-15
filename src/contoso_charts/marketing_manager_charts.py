import plotly.express as px
from plotly.graph_objects import Figure
import plotly.graph_objects as go

from contoso_charts.data import Model


def card_total_returns(model: Model) -> go.Figure:
    """Card: Returned Units = SUM(Fact_Sales[ReturnQuantity])"""
    total_returns = model.sales["ReturnQuantity"].sum()

    fig = go.Figure(
        go.Indicator(
            mode="number",
            value=total_returns,
            title={"text": "US-06: Totale retouren"},
            number={"valueformat": ",.0f"},
        )
    )
    fig.update_layout(height=200)
    return fig


def card_active_promotions(model: Model) -> go.Figure:
    """Card: number of promotions with a discount that run within the calendar period."""
    period_start = model.calendar["Date"].min()
    period_end = model.calendar["Date"].max()

    promotions = model.promotion
    promotions = promotions[promotions["StartDate"] <= period_end]
    promotions = promotions[promotions["EndDate"] >= period_start]
    promotions = promotions[promotions["DiscountPercent"] > 0]
    active_promotions = len(promotions)

    fig = go.Figure(
        go.Indicator(
            mode="number",
            value=active_promotions,
            title={"text": "US-06: Totaal aantal promoties"},
            number={"valueformat": ",.0f"},
        )
    )
    fig.update_layout(height=200)
    return fig


def card_total_discount(model: Model) -> go.Figure:
    """Card: Total Discount = SUM(Fact_Sales[DiscountAmount])"""
    total_discount = model.sales["DiscountAmount"].sum()

    fig = go.Figure(
        go.Indicator(
            mode="number",
            value=total_discount,
            title={"text": "US-06: Totale gegeven korting"},
            number={"prefix": "$", "valueformat": ",.0f"},
        )
    )
    fig.update_layout(height=200)
    return fig


def sales_with_promotion(model: Model) -> go.Figure:
    """US-07: monthly sales, split into sales with and without a promotion."""
    # 1. Take only the columns this chart needs
    sales = model.sales[["DateKey", "PromotionKey", "SalesAmount"]]
    calendar = model.calendar[["Date", "YearMonth"]]
    promotion = model.promotion[["PromotionKey", "Promotie Status"]]

    # 2. Look up the month and the promotion status for every sales row
    merged = sales.merge(calendar, left_on="DateKey", right_on="Date", how="left")
    merged = merged.merge(promotion, on="PromotionKey", how="left")

    # 3. Add up sales per month and promotion status
    per_month = merged.groupby(["YearMonth", "Promotie Status"], as_index=False)[
        "SalesAmount"
    ].sum()

    # 4. Build the figure
    fig = px.line(
        per_month,
        x="YearMonth",
        y="SalesAmount",
        color="Promotie Status",
        markers=True,
        title="US-07: Totale verkoop met promotie overzicht",
        labels={"YearMonth": "Maand", "SalesAmount": "Omzet"},
        hover_data={"SalesAmount": ":,.0f"},
        template="plotly_white",
    )
    fig.update_layout(height=650, yaxis_tickprefix="$")
    return fig


def best_selling_campaign(model: Model) -> go.Figure:
    """US-08: total sales per promotion, highest at the top."""
    # 1. Take only the columns this chart needs
    sales = model.sales[["PromotionKey", "SalesAmount"]]
    promotion = model.promotion[["PromotionKey", "PromotionName"]]

    # 2. Look up the promotion name for every sales row
    merged = sales.merge(promotion, on="PromotionKey", how="left")

    # 3. Leave out sales without a promotion
    merged = merged[merged["PromotionName"] != "No Discount"]

    # 4. Add up sales per promotion
    per_promotion = merged.groupby("PromotionName", as_index=False)["SalesAmount"].sum()

    # 5. Build the figure
    fig = px.bar(
        per_promotion,
        x="SalesAmount",
        y="PromotionName",
        orientation="h",
        title="US-08: Best verkopende campagne",
        labels={"SalesAmount": "Omzet", "PromotionName": "Campagne"},
        hover_data={"SalesAmount": ":,.0f"},
        template="plotly_white",
    )
    fig.update_yaxes(categoryorder="total ascending")
    fig.update_layout(height=650, xaxis_tickprefix="$")
    return fig


def sales_per_channel_and_region(model: Model) -> go.Figure:
    """US-09: total sales per continent, with one bar per channel."""
    # 1. Take only the columns this chart needs
    sales = model.sales[["channelKey", "StoreKey", "SalesAmount"]]
    channel = model.channel[["Channel", "ChannelName"]]
    stores = model.stores[["StoreKey", "GeographyKey"]]
    geography = model.geography[["GeographyKey", "ContinentName"]]

    # 2. Look up channel name and continent for every sales row
    merged = sales.merge(channel, left_on="channelKey", right_on="Channel", how="left")
    merged = merged.merge(stores, on="StoreKey", how="left")
    merged = merged.merge(geography, on="GeographyKey", how="left")

    # 3. Add up sales per continent and channel
    per_group = merged.groupby(["ContinentName", "ChannelName"], as_index=False)[
        "SalesAmount"
    ].sum()

    # 4. Build the figure
    fig = px.bar(
        per_group,
        x="ContinentName",
        y="SalesAmount",
        color="ChannelName",
        barmode="group",
        title="US-09: Verkoop per kanaal en regio",
        labels={"ContinentName": "Continent", "SalesAmount": "Omzet", "ChannelName": "Kanaal"},
        hover_data={"SalesAmount": ":,.0f"},
        template="plotly_white",
    )
    fig.update_xaxes(categoryorder="total descending")
    fig.update_layout(height=650, yaxis_tickprefix="$")
    return fig


def sales_per_category(model: Model) -> go.Figure:
    """US-10: treemap of sales per product category and subcategory."""
    # 1. Take only the columns this chart needs
    sales = model.sales[["ProductKey", "SalesAmount", "SalesQuantity"]]
    product = model.product[["ProductKey", "ProductSubcategoryKey"]]
    subcategory = model.product_subcategory[
        ["ProductSubcategoryKey", "ProductSubcategory", "ProductCategoryKey"]
    ]
    category = model.product_category[["ProductCategoryKey", "ProductCategory"]]

    # 2. Walk from product to subcategory to category
    merged = sales.merge(product, on="ProductKey", how="left")
    merged = merged.merge(subcategory, on="ProductSubcategoryKey", how="left")
    merged = merged.merge(category, on="ProductCategoryKey", how="left")

    # 3. Add up sales and units per subcategory
    per_subcategory = merged.groupby(["ProductCategory", "ProductSubcategory"], as_index=False)[
        ["SalesAmount", "SalesQuantity"]
    ].sum()

    # 4. Build the figure
    fig = px.treemap(
        per_subcategory,
        path=["ProductCategory", "ProductSubcategory"],
        values="SalesAmount",
        title="US-10: Verkoop per categorie",
        labels={"SalesAmount": "Omzet", "SalesQuantity": "Aantal verkocht"},
        hover_data={"SalesQuantity": ":,.0f"},
        template="plotly_white",
    )
    fig.update_traces(texttemplate="%{label}<br>$%{value:,.0f}")
    fig.update_layout(height=650)
    return fig


def discount_per_currency(model: Model) -> go.Figure:
    """US-11: average store discount % on promotion sales, per currency."""
    # 1. Take only the columns this chart needs
    sales = model.sales[["channelKey", "PromotionKey", "StoreKey", "SalesAmount", "DiscountAmount"]]
    channel = model.channel[["Channel", "ChannelName"]]
    promotion = model.promotion[["PromotionKey", "DiscountPercent"]]
    stores = model.stores[["StoreKey", "GeographyKey"]]
    geography = model.geography[["GeographyKey", "CurrencyCode"]]
    currency = model.currency[["CurrencyCode", "CurrencyName", "Currency Group"]]

    # 2. Look up channel, discount, and currency for every sales row
    merged = sales.merge(channel, left_on="channelKey", right_on="Channel", how="left")
    merged = merged.merge(promotion, on="PromotionKey", how="left")
    merged = merged.merge(stores, on="StoreKey", how="left")
    merged = merged.merge(geography, on="GeographyKey", how="left")
    merged = merged.merge(currency, on="CurrencyCode", how="left")

    # 3. Keep only Store sales that had a promotion with a discount
    filtered = merged[merged["ChannelName"] == "Store"]
    filtered = filtered[filtered["DiscountPercent"] > 0]

    # 4. Add up discount and sales per currency
    per_currency = filtered.groupby(["CurrencyName", "Currency Group"], as_index=False)[
        ["DiscountAmount", "SalesAmount"]
    ].sum()

    # 5. Calculate the discount percentage on the currency totals
    per_currency = per_currency.assign(
        DiscountPct=per_currency["DiscountAmount"] / per_currency["SalesAmount"]
    )

    # 6. Build the figure
    fig = px.bar(
        per_currency,
        x="CurrencyName",
        y="DiscountPct",
        color="Currency Group",
        title="US-11: Gemiddelde Kortings percentage per valuta",
        labels={"CurrencyName": "Valuta", "DiscountPct": "Korting %"},
        hover_data={"DiscountPct": ":.2%"},
        color_discrete_map={
            "Strengthened vs USD": "#3fb950",
            "Weakened vs USD": "#f85149",
            "No currency effect (USD)": "#8b949e",
        },
        template="plotly_white",
    )
    fig.update_xaxes(categoryorder="total descending")
    fig.update_layout(height=650, yaxis_tickformat=".1%")
    return fig
