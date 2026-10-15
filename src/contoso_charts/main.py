from contoso_charts.data import load_model


def main() -> None:
    model = load_model()
    print(model.sales.shape)
    print(model.sales.dtypes)
    print(model.product.head())


if __name__ == "__main__":
    main()
