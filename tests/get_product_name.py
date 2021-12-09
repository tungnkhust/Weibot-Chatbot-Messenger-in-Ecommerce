import pandas as pd


product_df = pd.read_csv("document/products_export_1.csv")

product_names = []
for _, row in product_df.iterrows():
    if isinstance(row["Title"], str):
        product_names.append(row["Title"])

df = pd.DataFrame({"Title": product_names})
df.to_csv("document/products_name.csv", index=False)