
import pandas as pd


df = pd.read_csv("third_party_vendor_risk_synthetic.csv")

print("FIRST 5 VENDORS")
print(df.head())

print("\nDataset dimensions:", df.shape)
print("\nColumn names:")
print(df.columns.tolist())




print("\nMISSING VALUES")
print(df.isnull().sum())

print("\nCOLUMN DATA TYPES")
print(df.dtypes)

print("\nDuplicate vendor IDs:",
      df["Vendor_ID"].duplicated().sum())

print("\nNUMERIC SUMMARY")
print(df.describe())

# Check whether overdue findings exceed open findings
invalid_findings = df[
    df["Overdue_Findings"] > df["Open_Findings"]
]

print("\nRecords with invalid findings counts:",
      len(invalid_findings))

# Check for negative numeric values
numeric_columns = [
    "Days_Since_Assessment",
    "Open_Findings",
    "Overdue_Findings"
]

print("\nNEGATIVE VALUES")
print((df[numeric_columns] < 0).sum())





criticality_points = {
    "High": 20,
    "Medium": 12,
    "Low": 5
}

df["Criticality_Score"] = (
    df["Business_Criticality"].map(criticality_points)
)

# Data sensitivity: maximum 20 points
sensitivity_points = {
    "High": 20,
    "Medium": 12,
    "Low": 5
}

df["Sensitivity_Score"] = (
    df["Data_Sensitivity"].map(sensitivity_points)
)

# ISO 27001 certification signal: maximum 10 points
df["ISO_Risk_Score"] = df["ISO27001_Certified"].map({
    "Yes": 0,
    "No": 10
})

# Multi-factor authentication signal: maximum 10 points
df["MFA_Risk_Score"] = df["MFA_Enabled"].map({
    "Yes": 0,
    "No": 10
})

# Open findings: maximum 15 points
df["Open_Findings_Score"] = (
    df["Open_Findings"].clip(upper=6) / 6 * 15
)

# Overdue findings: maximum 15 points
df["Overdue_Findings_Score"] = (
    df["Overdue_Findings"].clip(upper=6) / 6 * 15
)

# Assessment age: maximum 10 points
def score_assessment_age(days):
    if days <= 180:
        return 0
    elif days <= 365:
        return 5
    else:
        return 10

df["Assessment_Age_Score"] = (
    df["Days_Since_Assessment"].apply(score_assessment_age)
)



score_columns = [
    "Criticality_Score",
    "Sensitivity_Score",
    "ISO_Risk_Score",
    "MFA_Risk_Score",
    "Open_Findings_Score",
    "Overdue_Findings_Score",
    "Assessment_Age_Score"
]

df["Risk_Score"] = (
    df[score_columns].sum(axis=1).round(1)
)



def classify_risk(score):
    if score >= 70:
        return "High"
    elif score >= 40:
        return "Medium"
    else:
        return "Low"

df["Risk_Level"] = df["Risk_Score"].apply(classify_risk)



top_risk_vendors = df.sort_values(
    by="Risk_Score",
    ascending=False
)

print("\nTOP 10 VENDORS BY RISK SCORE")

print(
    top_risk_vendors[
        [
            "Vendor_ID",
            "Vendor_Category",
            "Business_Criticality",
            "Data_Sensitivity",
            "Open_Findings",
            "Overdue_Findings",
            "Risk_Score",
            "Risk_Level"
        ]
    ].head(10).to_string(index=False)
)



print("\nVENDOR COUNTS BY RISK LEVEL")

print(
    df["Risk_Level"]
    .value_counts()
    .reindex(["High", "Medium", "Low"], fill_value=0)
)



output_file = "vendor_risk_analysis.csv"

df.to_csv(output_file, index=False)

print("\nAnalysed data saved to:", output_file)
print("Total vendors analysed:", len(df))
print("Analysis completed successfully!")
