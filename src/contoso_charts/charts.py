import plotly.express as px
from plotly.graph_objects import Figure
import plotly.graph_objects as go

from contoso_charts.data import Model

def card_total_sales(model: Model) -> go.Figure:
    """Card: Total Sales = SUM(Fact_Sales[SalesAmount])"""
    total = model.sales["SalesAmount"].sum()

    fig = go.Figure(
        go.Indicator(
            mode="number",
            value=total,
            title={"text": "US-01: Totale verkoop"},
            number={"prefix": "$", "valueformat": ",.0f"},
        )
    )
    fig.update_layout(height=200)
    return fig

def card_total_cost(model: Model) -> go.Figure:
    """Card: Total Cost = SUM(Fact_Sales[TotalCost])"""
    total_cost = model.sales["TotalCost"].sum()

    fig = go.Figure(
        go.Indicator(
            mode="number",
            value=total_cost,
            title={"text": "US-01: Inkoopkosten"},
            number={"prefix": "$", "valueformat": ",.0f"},
        )
    )
    fig.update_layout(height=200)
    return fig


def card_total_profit(model: Model) -> go.Figure:
    """Card: Total Profit = [Total Sales] - [Total Cost]"""
    total_sales = model.sales["SalesAmount"].sum()
    total_cost = model.sales["TotalCost"].sum()
    total_profit = total_sales - total_cost

    fig = go.Figure(
        go.Indicator(
            mode="number",
            value=total_profit,
            title={"text": "US-01: Bruto winst"},
            number={"prefix": "$", "valueformat": ",.0f"},
        )
    )
    fig.update_layout(height=200)
    return fig


def card_margin(model: Model) -> go.Figure:
    """Card: Margin % = DIVIDE([Total Profit], [Total Sales])"""
    total_sales = model.sales["SalesAmount"].sum()
    total_cost = model.sales["TotalCost"].sum()
    margin = (total_sales - total_cost) / total_sales

    fig = go.Figure(
        go.Indicator(
            mode="number",
            value=margin,
            title={"text": "Bruto Marge %"},
            number={"valueformat": ".1%"},
        )
    )
    fig.update_layout(height=200)
    return fig

def revenue_year_over_year(model: Model) -> Figure:
    """US-02: revenue per quarter, with margin % in the tooltip."""
    # 1. Take only the columns this chart needs
    sales = model.sales[["DateKey", "SalesAmount", "TotalCost"]]
    calendar = model.calendar[["Date", "YearQuarter", "YearQuarterSort"]]

    # 2. Look up the quarter for every sales row
    merged = sales.merge(calendar, left_on="DateKey", right_on="Date", how="left")

    # 3. Add up sales and cost per quarter
    per_quarter = merged.groupby(["YearQuarterSort", "YearQuarter"], as_index=False)[
        ["SalesAmount", "TotalCost"]
    ].sum()

    # 4. Calculate the margin on the quarter totals
    per_quarter = per_quarter.assign(
        MarginPct=(per_quarter["SalesAmount"] - per_quarter["TotalCost"])
        / per_quarter["SalesAmount"]
    )

    # 5. Build the figure
    fig = px.line(
        per_quarter,
        x="YearQuarter",
        y="SalesAmount",
        markers=True,
        title="US-02: Jaar op Jaar omzet",
        labels={"YearQuarter": "Kwartaal", "SalesAmount": "Omzet", "MarginPct": "Marge %"},
        hover_data={"SalesAmount": ":,.0f", "MarginPct": ":.1%"},
        template="plotly_white",
    )
    fig.update_layout(height=650)
    return fig

def sales_margin_per_country(model: Model) -> go.Figure:
    """US-05: store sales (x) against margin % (y) per country, excluding the USA."""
    # 1. Take only the columns this chart needs
    sales = model.sales[["channelKey", "StoreKey", "SalesAmount", "TotalCost"]]
    channel = model.channel[["Channel", "ChannelName"]]
    stores = model.stores[["StoreKey", "GeographyKey"]]
    geography = model.geography[["GeographyKey", "RegionCountryName"]]

    # 2. Look up channel name and country for every sales row
    merged = sales.merge(channel, left_on="channelKey", right_on="Channel", how="left")
    merged = merged.merge(stores, on="StoreKey", how="left")
    merged = merged.merge(geography, on="GeographyKey", how="left")

    # 3. Keep only Store sales, and leave out the USA
    filtered = merged[merged["ChannelName"] == "Store"]
    filtered = filtered[filtered["RegionCountryName"] != "United States"]

    # 4. Add up sales and cost per country
    per_country = filtered.groupby("RegionCountryName", as_index=False)[
        ["SalesAmount", "TotalCost"]
    ].sum()

    # 5. Calculate the margin on the country totals
    per_country = per_country.assign(
        MarginPct=(per_country["SalesAmount"] - per_country["TotalCost"])
        / per_country["SalesAmount"]
    )

    # 6. Build the figure
    fig = px.scatter(
        per_country,
        x="SalesAmount",
        y="MarginPct",
        hover_name="RegionCountryName",
        title="US-05: Totale verkoop en marge per land",
        labels={"SalesAmount": "Omzet (winkels)", "MarginPct": "Marge %"},
        hover_data={"SalesAmount": ":,.0f", "MarginPct": ":.1%"},
        template="plotly_white",
    )
    fig.update_traces(marker={"size": 10})
    fig.update_layout(height=650, xaxis_tickprefix="$", yaxis_tickformat=".0%")
    return fig

FIRST_YEAR = 2011
LAST_YEAR = 2013


def exchange_rate_vs_sales(model: Model) -> go.Figure:
    """US-03: change in exchange rate (x) against change in store sales (y) per currency."""
    # 1. Take only the columns this chart needs
    sales = model.sales[["DateKey", "channelKey", "StoreKey", "SalesAmount"]]
    channel = model.channel[["Channel", "ChannelName"]]
    stores = model.stores[["StoreKey", "GeographyKey"]]
    geography = model.geography[["GeographyKey", "CurrencyCode"]]
    rates = model.exchange_rate[["YearMonth", "CurrencyCode", "USDPerUnit"]]

    # 2. Look up channel name and currency for every sales row
    merged = sales.merge(channel, left_on="channelKey", right_on="Channel", how="left")
    merged = merged.merge(stores, on="StoreKey", how="left")
    merged = merged.merge(geography, on="GeographyKey", how="left")

    # 3. Keep only Store sales outside the USD, and add the year
    filtered = merged[merged["ChannelName"] == "Store"]
    filtered = filtered[filtered["CurrencyCode"] != "USD"]
    filtered = filtered.assign(Year=filtered["DateKey"].dt.year)

    # 4. Sales change per currency: last year compared with first year
    sales_first = filtered[filtered["Year"] == FIRST_YEAR].groupby("CurrencyCode")["SalesAmount"].sum()
    sales_last = filtered[filtered["Year"] == LAST_YEAR].groupby("CurrencyCode")["SalesAmount"].sum()
    sales_change = ((sales_last - sales_first) / sales_first).reset_index(name="SalesChange")

    # 5. Exchange-rate change per currency: average of last year compared with first year
    rates = rates.assign(Year=rates["YearMonth"].dt.year)
    rate_first = rates[rates["Year"] == FIRST_YEAR].groupby("CurrencyCode")["USDPerUnit"].mean()
    rate_last = rates[rates["Year"] == LAST_YEAR].groupby("CurrencyCode")["USDPerUnit"].mean()
    rate_change = ((rate_last - rate_first) / rate_first).reset_index(name="RateChange")

    # 6. Combine into one row per currency
    per_currency = rate_change.merge(sales_change, on="CurrencyCode", how="inner")

    # 7. Build the figure
    fig = px.scatter(
        per_currency,
        x="RateChange",
        y="SalesChange",
        text="CurrencyCode",
        title="US-03: Totale verkoop vergeleken met wisselkoers",
        labels={
            "RateChange": "Verandering wisselkoers t.o.v. USD",
            "SalesChange": "Verandering winkelomzet",
            "CurrencyCode": "Valuta",
        },
        hover_data={"RateChange": ":.1%", "SalesChange": ":.1%"},
        template="plotly_white",
    )
    fig.update_traces(marker={"size": 10}, textposition="top center")
    fig.add_hline(y=0, line_dash="dot", line_color="grey")
    fig.add_vline(x=0, line_dash="dot", line_color="grey")
    fig.update_layout(height=650, xaxis_tickformat=".0%", yaxis_tickformat=".0%")
    return fig


def exchange_rate_volatility(model: Model) -> go.Figure:
    """US-04: exchange-rate volatility per currency against the USD."""
    # 1. Take only the columns this chart needs
    currency = model.currency[["CurrencyCode", "CurrencyName", "Currency Group"]]
    rates = model.exchange_rate[["CurrencyCode", "USDPerUnit"]]
    geography = model.geography[["CurrencyCode", "RegionCountryName"]]

    # 2. Volatility per currency: standard deviation divided by the average
    rates_per_currency = rates.groupby("CurrencyCode")["USDPerUnit"]
    volatility = rates_per_currency.std(ddof=0) / rates_per_currency.mean()
    volatility = volatility.reset_index(name="Volatility")

    # 3. Countries per currency, as one comma-separated text
    countries = geography.sort_values("RegionCountryName")
    countries = countries.groupby("CurrencyCode")["RegionCountryName"].agg(", ".join)
    countries = countries.reset_index(name="Countries")

    # 4. Combine everything into one row per currency, without the USD
    currency = currency[currency["CurrencyCode"] != "USD"]
    per_currency = currency.merge(volatility, on="CurrencyCode", how="left")
    per_currency = per_currency.merge(countries, on="CurrencyCode", how="left")

    # 5. Build the figure
    fig = px.bar(
        per_currency,
        x="CurrencyCode",
        y="Volatility",
        color="Currency Group",
        hover_name="CurrencyName",
        hover_data={"Volatility": ":.1%", "Countries": True, "CurrencyCode": False},
        title="US-04: Wisselkoersschommeling per valuta (Vergeleken met USD)",
        labels={"CurrencyCode": "Valuta", "Volatility": "Schommeling %", "Countries": "Landen"},
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