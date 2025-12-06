#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Converted from Jupyter Notebook: notebook.ipynb
Conversion Date: 2025-12-06T06:11:30.803Z
"""

# open llm_pr_labeled dataset from path
import pandas as pd
df2 = pd.read_csv('llm_pr_labeled.csv')  # Update this path to your dataset location


df2.columns

df2.shape


# Filter only ChatgptSharing = True
df_llm = df2[df2["ChatgptSharing"] == True].copy()

print("LLM-only shape:", df_llm.shape)


# merged at prs State
df_llm[df_llm["MergedAt"].notnull()]["State"].value_counts()


# Unique state in the df_llm
df_llm["State"].unique()

df_llm.loc[df_llm["MergedAt"].notnull(), "State"] = "merged"

# Unique state in the df_llm
df_llm["State"].unique()

# values counts of State
df_llm["State"].value_counts()

# make a csv named craweled_pr with only the rows where ChatgptSharing is True
df_llm.to_csv('crawled_pr.csv', index=False)

df_llm.head()

df_llm.shape

# open data from another path
df1 = pd.read_csv('PR_dataset.csv')  # Update this path to your dataset location

df1.shape

df1.columns

# identify common columns
common_cols = set(df1.columns).intersection(set(df_llm.columns))
len(common_cols)

# merge datasets on common columns
merged_df = pd.merge(df1, df_llm, on=list(common_cols), how='outer')   


merged_df.shape

merged_df.head()

# unique values in State column
merged_df["State"].unique()

# make a csv with the merged dataset
merged_df.to_csv('combined_dataset.csv', index=False)
