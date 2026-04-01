import pandas as pd
pd.set_option("display.max_columns", None)  # show all columns

df = pd.read_csv("results_table.csv")

print("\n=== SUMMARY ===")

print("\nTotal circuits:", len(df))
print("LLM circuits:", df["LLM"].sum())

print("\nVulnerability rate:")
print(df.groupby("LLM")["vulnerable"].mean())

print("\nAverage TVD:")
print(df.groupby("LLM")["tvd"].mean())

print("\nRule counts:")
print(df[["R1", "R2", "R3", "R4", "R5", "RV1"]].sum())

#  OPTIONAL BUT VERY USEFUL 
print("\nRule rates:")
print(df[["R1", "R2", "R3", "R4", "R5", "RV1"]].mean())

print("\nRule rates by LLM:")
print(df.groupby("LLM")[["R1", "R2", "R3", "R4", "R5", "RV1"]].mean())