import os

circuits = set(
    f.split("/")[-1].split(".")[0]
    for f in os.listdir("circuits")
)

reports = set(
    f.replace(".json", "")
    for f in os.listdir("reports")
)

missing = circuits - reports

print("Not processed:", missing)