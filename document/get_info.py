import pandas as pd


product_df = pd.read_csv("document/products_export_1.csv")

values = []
for _, row in product_df.iterrows():
    if isinstance(row["Option2 Value"], str):
        values.append(row["Option2 Value"])

values = list(set(values))
df = pd.DataFrame({"Title": values})
df.to_csv("document/object_type.csv", index=False)