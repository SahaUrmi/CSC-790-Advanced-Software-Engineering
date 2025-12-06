#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Converted from Jupyter Notebook: notebook.ipynb
Conversion Date: 2025-12-06T06:08:15.751Z
"""

import pandas as pd

# Load the labeled dataset
df_llm = pd.read_csv("crawled_pr.csv")  # Update this path to your dataset location

print("Dataset shape:", df_llm.shape)
df_llm.head()

df_llm[["CreatedAt", "UpdatedAt", "MergedAt"]].notnull().sum()

# merged at prs State
df_llm[df_llm["MergedAt"].notnull()]["State"].value_counts()


# 5 merged at prs url
df_llm[df_llm["MergedAt"].notnull()]["URL"].head()

# Unique state in the df_llm
df_llm["State"].unique()

# values counts of State
df_llm["State"].value_counts()

# make everything lowercase in the State column
df_llm["State"] = df_llm["State"].str.lower()

# values counts of State
df_llm["State"].value_counts()

# show 10 url open prs
df_llm[df_llm["State"] == "open"]["URL"].head(10)


import matplotlib.pyplot as plt
import seaborn as sns
# Plot Bar plot for PR states
pr_state_counts = df_llm['State'].value_counts()
plt.figure(figsize=(8,5))
# give merge light green color, open sky blue color, closed light pink red color
palette = {'merged': 'lightgreen', 'open': 'skyblue', 'closed': 'lightcoral'}
sns.barplot(x=pr_state_counts.index, y=pr_state_counts.values, palette=palette)
plt.title('Pull Request States')
plt.xlabel('State')
plt.ylabel('Number of Pull Requests')
plt.xticks(rotation=45)
plt.show()

merged_prs = df_llm[df_llm["State"] == "merged"]
print("Number of merged PRs:", merged_prs.shape[0])
closed_prs = df_llm[df_llm["State"] == "closed"]
print("Number of closed PRs:", closed_prs.shape[0])
open_prs = df_llm[df_llm["State"] == "open"]
print("Number of open PRs:", open_prs.shape[0])


# #### Metric 1: Time to Integartion for Merged Commits


# Calculate merged pull request time-to-integration from created to merged in hours and if it is more than 24 hours keep those records in a set for further analysis
merged_prs['CreatedAt'] = pd.to_datetime(merged_prs['CreatedAt'])
merged_prs['MergedAt'] = pd.to_datetime(merged_prs['MergedAt'])
merged_prs['TimeToMergeHours'] = (merged_prs['MergedAt'] - merged_prs['CreatedAt']).dt.total_seconds() / 3600
#print hours with repos, created and merged time
print(merged_prs[['RepoName', 'CreatedAt', 'MergedAt', 'TimeToMergeHours']].head(10))

#print head of merged_prs with only TimeToMergeHours column
# print(merged_prs[['RepoName', 'TimeToMergeHours']].head(10))
# average time to merge
average_time_to_merge = merged_prs['TimeToMergeHours'].mean()
print("Average Time to Merge (hours):", average_time_to_merge)  
# Categorize PRs with (1hour to 2 hours), (2 hours to 4 hours), (8 hours to 24 hours), (half a week : 3 days), (more than 3 days to 7 days or more)
    
# Apply categorization to ascending order of scale hours first, days later
def categorize_prs(row):    
    hours = row['TimeToMergeHours']

    if 0 < hours <= 2:
        return '1-2 hours'
    elif 2 < hours <= 4:
        return '2-4 hours'
    elif 4 < hours <= 8:
        return '4-8 hours'
    elif 8 < hours <= 24:
        return '8 hours - 1 day'
    elif 24 < hours <= 72:
        return 'half a week : 1-3 days'
    elif 72 < hours < 168:
        return 'almost a week : 3-7 days'
    else:
        return 'More than 7 days'

# Apply the categorization function
merged_prs['MergeTimeCategory'] = merged_prs.apply(categorize_prs, axis=1)


# Plot the distribution of PRs by MergeTimeCategory 
# first all the hours categories then days categories
category_order = ['1-2 hours', '2-4 hours', '4-8 hours', '8 hours - 1 day', 'half a week : 1-3 days', 'almost a week : 3-7 days', 'More than 7 days']
merged_prs['MergeTimeCategory'] = pd.Categorical(merged_prs['MergeTimeCategory'], categories=category_order, ordered=True)      
plt.figure(figsize=(12,6))
# use a differnet nice coloer palette

sns.countplot(data=merged_prs, x='MergeTimeCategory', order=category_order, palette='Set2')
plt.title('DevLLM: Distribution of Merged PRs by Time-to-Integration Categories')
plt.xlabel('Time-to-Integration Category')
plt.ylabel('Number of Merged PRs')
plt.xticks(rotation=45)
plt.show()

# # average time to merge per RepoLanguage
# average_time_by_language = merged_prs.groupby('RepoLanguage')['TimeToMergeHours'].mean().sort_values()
# print("Average Time to Merge by RepoLanguage:\n", average_time_by_language)

# minimumand maximum time to merge 
min_time_to_merge = merged_prs['TimeToMergeHours'].min()
max_time_to_merge = merged_prs['TimeToMergeHours'].max()
print("Minimum Time to Merge (hours):", min_time_to_merge)
print("Maximum Time to Merge (hours):", max_time_to_merge)
# long_merge_prs = merged_prs[merged_prs['TimeToMergeHours'] > 24]
# print("Total PRs with TimeToMergeHours > 24:", len(long_merge_prs))


# identify all the tokens from Title column of the merged_prs DataFrame
import re
from collections import Counter     
title_tokens = []
for title in merged_prs['Title'].dropna():
    # tokenize by non-alphanumeric characters
    tokens = re.findall(r'\b\w+\b', title.lower())
    title_tokens.extend(tokens)     
    #print the number of tokens extracted
print("Total tokens extracted from Titles:", len(title_tokens))

# find how many distinct merged prs contain readme words in the title
distinct_readme_prs = merged_prs[merged_prs['Title'].str.contains('readme', case=False, na=False)]
print("Number of distinct merged PRs containing 'readme' in the title:", distinct_readme_prs.shape[0])  


# find readme words in any case upper or lower case or mixed case
readme_tokens = [token for token in title_tokens if 'readme' in token.lower()]  
print("------"*15)       
print("Total 'readme' tokens extracted from Titles:", len(readme_tokens)) 
print("------"*15)
# print unique readme tokens
print("Unique 'readme' tokens in Titles:", set(readme_tokens))
# show those prs
print("------"*15)
print("Distinct merged PRs containing 'readme' in the title:\n", distinct_readme_prs[['RepoName', 'Title']])    
print("------"*15)


# identify the verb tokens from the title_tokens list
from nltk.corpus import wordnet
import nltk     
# nltk.download('wordnet')
# nltk.download('omw-1.4')
verb_tokens = [token for token in title_tokens if wordnet.synsets(token, pos=wordnet.VERB)]
print("Total verb tokens extracted from Titles:", len(verb_tokens)) 
# Show verb containing repos and titles head
# print(merged_prs[merged_prs['Title'].str.contains('|'.join(set(verb_tokens)), case=False, na=False)][['RepoName', 'Title']].head(10))   

# all the unoque verb tokens
unique_verb_tokens = set(verb_tokens)
print("Unique verb tokens in Titles:", unique_verb_tokens)
print("Total unique verb tokens in Titles:", len(unique_verb_tokens))

# Count Title if it contains verb in the beginning position 
beginning_verb_titles = merged_prs[merged_prs['Title'].str.contains('|'.join(set(verb_tokens)), case=False, na=False)]
print("Total merged PRs with verbs in the beginning of the title:", beginning_verb_titles.shape[0])
# show those prs titles with verbs in the beginning
print("------"*15)
print("Merged PRs with verbs in the beginning of the title:\n", beginning_verb_titles[['RepoName', 'Title']].head(10))
print("------"*15)  
    
# How many unique verb in those prs Title's beginning position
unique_beginning_verb_tokens = set(token for title in beginning_verb_titles['Title'] for token in title.split() if token in unique_verb_tokens)
print("Unique verb tokens in the beginning of Titles:", unique_beginning_verb_tokens)
print("Total unique verb tokens in the beginning of Titles:", len(unique_beginning_verb_tokens))
# verb dictionary
verbs = list(unique_beginning_verb_tokens)



# How many unique nouns in those prs Title's second position

from nltk.corpus import wordnet
noun_tokens = [token for token in title_tokens if wordnet.synsets(token, pos=wordnet.NOUN)]
print("Total noun tokens extracted from Titles:", len(noun_tokens)) 
# unique noun tokens
unique_noun_tokens = set(noun_tokens)
print("Total unique noun tokens in Titles:", len(unique_noun_tokens))  
# show those prs titles with nouns in the second position
# print("------"*15)
# print("Merged PRs with nouns in the second position of the title:\n", merged_prs[merged_prs['Title'].str.contains('|'.join(set(noun_tokens)), case=False, na=False)][['RepoName', 'Title']].head(10))
# print("------"*15)

# How many unique nouns in those prs Title's second position
# unique_second_noun_tokens = set(token for title in merged_prs['Title'] for token in title.split() if token in unique_noun_tokens)
# print("Unique noun tokens in the second position of Titles:", unique_second_noun_tokens)
# print("Total unique noun tokens in the second position of Titles:", len(unique_second_noun_tokens))

nouns = list(unique_noun_tokens)

# identify the adjective tokens from the title_tokens list
from nltk.corpus import wordnet
adj_tokens = [token for token in title_tokens if wordnet.synsets(token, pos=wordnet.ADJ)]
print("Total adjective tokens extracted from Titles:", len(adj_tokens))
# show those prs titles with adjectives
# print("------"*15)
# print("Merged PRs with adjectives in the title:\n", merged_prs[merged_prs['Title'].str.contains('|'.join(set(adj_tokens)), case=False, na=False)][['RepoName', 'Title']].head(10))
# print("------"*15)
# unique adjective tokens
unique_adj_tokens = set(adj_tokens)
print("Total unique adjective tokens in Titles:", len(unique_adj_tokens))
adjectives = list(unique_adj_tokens)

# identify the adverb tokens from the title_tokens list
from nltk.corpus import wordnet
adv_tokens = [token for token in title_tokens if wordnet.synsets(token, pos=wordnet.ADV)]
print("Total adverb tokens extracted from Titles:", len(adv_tokens))
# show those prs titles with adverbs
# print("------"*15)
# print("Merged PRs with adverbs in the title:\n", merged_prs[merged_prs['Title'].str.contains('|'.join(set(adv_tokens)), case=False, na=False)][['RepoName', 'Title']].head(10))
# print("------"*15)
# unique adverb tokens
unique_adv_tokens = set(adv_tokens)
print("Total unique adverb tokens in Titles:", len(unique_adv_tokens))
adverbs = list(unique_adv_tokens)

# from verb noun adj and adverb build a pos map
pos_map = {
    "VERB": verbs,
    "NOUN": nouns,
    "ADJ": adjectives,
    "ADV": adverbs
}

import json
with open("pos_map.json", "w") as f:
    # convert to json file
    json.dump(pos_map, f, indent=4)


# # Corrected POS tags for each reason
# pos_tags = {
#     "bug_fix": ["VB", "NN"],
#     "feature_request": ["VB", "NN"],
#     "documentation": ["NN", "NN"],
#     "refactor": ["VB", "NN"],
#     "testing": ["NN", "NN"],
#     "dependency_update": ["NN", "NN"],
#     "performance": ["NN", "NN"],
#     "code_quality": ["NN", "NN"],
#     "security": ["NN", "NN"],
#     "ui_ux": ["NN", "NN"],
#     "api_change": ["NN", "NN"],
#     "build_configuration": ["NN", "NN"],
#     "localization": ["NN", "NN"],
#     "accessibility": ["NN", "NN"],
#     "miscellaneous": ["NN", "NN"]
# }

# # Create a dictionary that maps POS tags to words for the respective reason
# reason_based_words = {reason: [] for reason in pos_tags.keys()}

# for title in merged_prs['Title']:
#     # Tokenize the title
#     tokens = nltk.word_tokenize(title)
#     # Get POS tags for each token
#     pos_tagged_tokens = nltk.pos_tag(tokens)
    
#     # For each reason, check if the title matches the expected POS pattern
#     for reason, expected_pos in pos_tags.items():
#         if len(pos_tagged_tokens) >= len(expected_pos):
#             match = all(pos_tagged_tokens[i][1].startswith(expected_pos[i]) for i in range(len(expected_pos)))
#             if match:
#                 reason_based_words[reason].extend([word for word, pos in pos_tagged_tokens[:len(expected_pos)]])

# # Print the result
# for reason, words in reason_based_words.items():
#     print(f"{reason}: {set(words)}")


# show time to merge distribution median, mean, min, max, and std
print("Time to Merge (hours) Statistics:")
print("Median:", merged_prs['TimeToMergeHours'].median())
print("Mean:", merged_prs['TimeToMergeHours'].mean())
print("Min:", merged_prs['TimeToMergeHours'].min())
print("Max:", merged_prs['TimeToMergeHours'].max())
print("Std:", merged_prs['TimeToMergeHours'].std())


# #### Metric 2: PR Update Interval for Merged Commits


# if a merged PR has no update, that means it was merged directly, so time is 0
# if a merged PR has at least one update, then calculate the time difference between the created and the last update
merged_prs['UpdatedAt'] = pd.to_datetime(merged_prs['UpdatedAt'])
merged_prs['PRUpdateInterval'] = (merged_prs['UpdatedAt'] - merged_prs['CreatedAt']).dt.total_seconds() / 3600
# show the number of PRs with no update
print("Number of merged PRs with no update:", merged_prs[merged_prs['PRUpdateInterval'] == 0].shape[0])
# show the number of PRs with at least one update
print("Number of merged PRs with at least one update:", merged_prs[merged_prs['PRUpdateInterval'] > 0].shape[0])
# show the average update interval
print("Average PR Update Interval (hours):", merged_prs['PRUpdateInterval'].mean())
# show the median update interval
print("Median PR Update Interval (hours):", merged_prs['PRUpdateInterval'].median())
# show the minimum update interval
print("Minimum PR Update Interval (hours):", merged_prs['PRUpdateInterval'].min())
# show the maximum update interval
print("Maximum PR Update Interval (hours):", merged_prs['PRUpdateInterval'].max())
# show the standard deviation of the update interval
print("Std PR Update Interval (hours):", merged_prs['PRUpdateInterval'].std())


# categorize prs based on the Update Interval
# if Update Interval is 0, then it is a direct merge
# if Update Interval is between 0 and 2 hours, then it is a quick update
# if Update Interval is between 2 and 4 hours, then it is a moderate update
# if Update Interval is between 4 and 8 hours, then it is a slow update
# if Update Interval is between 8 and 24 hours, then it is a day update
# if Update Interval is between 24 and 72 hours, then it is a half-week update
# if Update Interval is between 72 and 168 hours, then it is a week update
# if Update Interval is more than 168 hours, then it is a long update

def categorize_update_interval(row):
    hours = row['PRUpdateInterval']
    if hours == 0:
        return 'Direct merge'
    elif 0 < hours <= 2:
        return '0-2 hours'
    elif 2 < hours <= 4:
        return '2-4 hours'
    elif 4 < hours <= 8:
        return '4-8 hours'
    elif 8 < hours <= 24:
        return '8 hours - 1 day'
    elif 24 < hours <= 72:
        return 'half a week : 1-3 days'
    elif 72 < hours < 168:
        return 'almost a week : 3-7 days'
    else:
        return 'More than 7 days'
    
merged_prs['UpdateIntervalCategory'] = merged_prs.apply(categorize_update_interval, axis=1)

# Plot the distribution of PRs by UpdateIntervalCategory
category_order = ['Direct merge', '0-2 hours', '2-4 hours', '4-8 hours', '8 hours - 1 day', 'half a week : 1-3 days', 'almost a week : 3-7 days', 'More than 7 days']
merged_prs['UpdateIntervalCategory'] = pd.Categorical(merged_prs['UpdateIntervalCategory'], categories=category_order, ordered=True)
plt.figure(figsize=(12,6))
sns.countplot(data=merged_prs, x='UpdateIntervalCategory', order=category_order, palette='Set2')
plt.title('DevLLM: Distribution of Merged PRs by Update Interval Categories')
plt.xlabel('Update Interval Category')
plt.ylabel('Number of Merged PRs')
plt.xticks(rotation=45)
plt.show()


# #### Metric 3: Number of Commits per PR


# identify the number of commits per PR for merged PRs
# merged_prs['Number_of_Commits'].describe()
# show the number of PRs with 1 commit
print("Number of merged PRs with 1 commit:", merged_prs[merged_prs['Number_of_Commits'] == 1].shape[0])
# show the number of PRs with more than 1 commit
print("Number of merged PRs with more than 1 commit:", merged_prs[merged_prs['Number_of_Commits'] > 1].shape[0])
# show the average number of commits per PR
print("Average Number of Commits per PR:", merged_prs['Number_of_Commits'].mean())
# show the median number of commits per PR
print("Median Number of Commits per PR:", merged_prs['Number_of_Commits'].median())
# show the minimum number of commits per PR
print("Minimum Number of Commits per PR:", merged_prs['Number_of_Commits'].min())
# show the maximum number of commits per PR
print("Maximum Number of Commits per PR:", merged_prs['Number_of_Commits'].max())
# show the standard deviation of the number of commits per PR
print("Std Number of Commits per PR:", merged_prs['Number_of_Commits'].std())

# categorize prs based on the number of commits
# if Number of Commits is 1, then it is a single commit PR
# if Number of Commits is between 2 and 5, then it is a small PR
# if Number of Commits is between 6 and 10, then it is a medium PR
# if Number of Commits is more than 10, then it is a large PR

def categorize_commits(row):
    commits = row['Number_of_Commits']
    if commits == 1:
        return 'Single commit'
    elif 2 <= commits <= 5:
        return '2-5 commits'
    elif 6 <= commits <= 10:
        return '6-10 commits'
    else:
        return 'More than 10 commits'
    
merged_prs['CommitsCategory'] = merged_prs.apply(categorize_commits, axis=1)

# Plot the distribution of PRs by CommitsCategory
category_order = ['Single commit', '2-5 commits', '6-10 commits', 'More than 10 commits']
merged_prs['CommitsCategory'] = pd.Categorical(merged_prs['CommitsCategory'], categories=category_order, ordered=True)
plt.figure(figsize=(12,6))
sns.countplot(data=merged_prs, x='CommitsCategory', order=category_order, palette='Set2')
plt.title('DevLLM: Distribution of Merged PRs by Number of Commits Categories')
plt.xlabel('Commits Category')
plt.ylabel('Number of Merged PRs')
plt.xticks(rotation=45)
plt.show()


# #### Metric 4: Changed Files Count per PR


# identify the number of changed files per PR for merged PRs
# merged_prs['Changed_Files_Count'].describe()
# show the number of PRs with 1 changed file
print("Number of merged PRs with 1 changed file:", merged_prs[merged_prs['Changed_Files_Count'] == 1].shape[0])
# show the number of PRs with more than 1 changed file
print("Number of merged PRs with more than 1 changed file:", merged_prs[merged_prs['Changed_Files_Count'] > 1].shape[0])
# show the average number of changed files per PR
print("Average Number of Changed Files per PR:", merged_prs['Changed_Files_Count'].mean())
# show the median number of changed files per PR
print("Median Number of Changed Files per PR:", merged_prs['Changed_Files_Count'].median())
# show the minimum number of changed files per PR
print("Minimum Number of Changed Files per PR:", merged_prs['Changed_Files_Count'].min())
# show the maximum number of changed files per PR
print("Maximum Number of Changed Files per PR:", merged_prs['Changed_Files_Count'].max())
# show the standard deviation of the number of changed files per PR
print("Std Number of Changed Files per PR:", merged_prs['Changed_Files_Count'].std())

# categorize prs based on the number of changed files
# if Number of Changed Files is 1, then it is a single file PR
# if Number of Changed Files is between 2 and 5, then it is a small PR
# if Number of Changed Files is between 6 and 10, then it is a medium PR
# if Number of Changed Files is more than 10, then it is a large PR

def categorize_changed_files(row):
    files = row['Changed_Files_Count']
    if files == 1:
        return 'Single file'
    elif 2 <= files <= 5:
        return '2-5 files'
    elif 6 <= files <= 10:
        return '6-10 files'
    else:
        return 'More than 10 files'
    
merged_prs['ChangedFilesCategory'] = merged_prs.apply(categorize_changed_files, axis=1)

# Plot the distribution of PRs by ChangedFilesCategory
category_order = ['Single file', '2-5 files', '6-10 files', 'More than 10 files']
merged_prs['ChangedFilesCategory'] = pd.Categorical(merged_prs['ChangedFilesCategory'], categories=category_order, ordered=True)
plt.figure(figsize=(12,6))
sns.countplot(data=merged_prs, x='ChangedFilesCategory', order=category_order, palette='Set2')
plt.title('DevLLM: Distribution of Merged PRs by Changed Files Categories')
plt.xlabel('Changed Files Category')
plt.ylabel('Number of Merged PRs')
plt.xticks(rotation=45)
plt.show()


# Metric 5: Lines of Code Added per PR


# identify the number of lines added per PR for merged PRs
# merged_prs['Lines_Added'].describe()
# show the number of PRs with 1 line added
print("Number of merged PRs with 1 line added:", merged_prs[merged_prs['Lines_Added'] == 1].shape[0])
# show the number of PRs with more than 1 line added
print("Number of merged PRs with more than 1 line added:", merged_prs[merged_prs['Lines_Added'] > 1].shape[0])
# show the average number of lines added per PR
print("Average Number of Lines Added per PR:", merged_prs['Lines_Added'].mean())
# show the median number of lines added per PR
print("Median Number of Lines Added per PR:", merged_prs['Lines_Added'].median())
# show the minimum number of lines added per PR
print("Minimum Number of Lines Added per PR:", merged_prs['Lines_Added'].min())
# show the maximum number of lines added per PR
print("Maximum Number of Lines Added per PR:", merged_prs['Lines_Added'].max())
# show the standard deviation of the number of lines added per PR
print("Std Number of Lines Added per PR:", merged_prs['Lines_Added'].std())

# categorize prs based on the number of lines added
# if Number of Lines Added is 1, then it is a single line PR
# if Number of Lines Added is between 2 and 10, then it is a small PR
# if Number of Lines Added is between 11 and 50, then it is a medium PR
# if Number of Lines Added is more than 50, then it is a large PR

def categorize_lines_added(row):
    lines = row['Lines_Added']
    if lines == 1:
        return 'Single line'
    elif 2 <= lines <= 10:
        return '2-10 lines'
    elif 11 <= lines <= 50:
        return '11-50 lines'
    else:
        return 'More than 50 lines'
    
merged_prs['LinesAddedCategory'] = merged_prs.apply(categorize_lines_added, axis=1)

# Plot the distribution of PRs by LinesAddedCategory
category_order = ['Single line', '2-10 lines', '11-50 lines', 'More than 50 lines']
merged_prs['LinesAddedCategory'] = pd.Categorical(merged_prs['LinesAddedCategory'], categories=category_order, ordered=True)
plt.figure(figsize=(12,6))
sns.countplot(data=merged_prs, x='LinesAddedCategory', order=category_order, palette='Set2')
plt.title('DevLLM: Distribution of Merged PRs by Lines Added Categories')
plt.xlabel('Lines Added Category')
plt.ylabel('Number of Merged PRs')
plt.xticks(rotation=45)
plt.show()


# Metric 6: Lines of Code Deleted per PR


# identify the number of lines deleted per PR for merged PRs
# merged_prs['Lines_Deleted'].describe()
# show the number of PRs with 1 line deleted
print("Number of merged PRs with 1 line deleted:", merged_prs[merged_prs['Lines_Deleted'] == 1].shape[0])
# show the number of PRs with more than 1 line deleted
print("Number of merged PRs with more than 1 line deleted:", merged_prs[merged_prs['Lines_Deleted'] > 1].shape[0])
# show the average number of lines deleted per PR
print("Average Number of Lines Deleted per PR:", merged_prs['Lines_Deleted'].mean())
# show the median number of lines deleted per PR
print("Median Number of Lines Deleted per PR:", merged_prs['Lines_Deleted'].median())
# show the minimum number of lines deleted per PR
print("Minimum Number of Lines Deleted per PR:", merged_prs['Lines_Deleted'].min())
# show the maximum number of lines deleted per PR
print("Maximum Number of Lines Deleted per PR:", merged_prs['Lines_Deleted'].max())
# show the standard deviation of the number of lines deleted per PR
print("Std Number of Lines Deleted per PR:", merged_prs['Lines_Deleted'].std())

# categorize prs based on the number of lines deleted
# if Number of Lines Deleted is 1, then it is a single line PR
# if Number of Lines Deleted is between 2 and 10, then it is a small PR
# if Number of Lines Deleted is between 11 and 50, then it is a medium PR
# if Number of Lines Deleted is more than 50, then it is a large PR

def categorize_lines_deleted(row):
    lines = row['Lines_Deleted']
    if lines == 1:
        return 'Single line'
    elif 2 <= lines <= 10:
        return '2-10 lines'
    elif 11 <= lines <= 50:
        return '11-50 lines'
    else:
        return 'More than 50 lines'
    
merged_prs['LinesDeletedCategory'] = merged_prs.apply(categorize_lines_deleted, axis=1)

# Plot the distribution of PRs by LinesDeletedCategory
category_order = ['Single line', '2-10 lines', '11-50 lines', 'More than 50 lines']
merged_prs['LinesDeletedCategory'] = pd.Categorical(merged_prs['LinesDeletedCategory'], categories=category_order, ordered=True)
plt.figure(figsize=(12,6))
sns.countplot(data=merged_prs, x='LinesDeletedCategory', order=category_order, palette='Set2')
plt.title('DevLLM: Distribution of Merged PRs by Lines Deleted Categories')
plt.xlabel('Lines Deleted Category')
plt.ylabel('Number of Merged PRs')
plt.xticks(rotation=45)
plt.show()


# #### General Analysis


# plot together in one figure side by side the committscategory, changedfilescategory, linesaddedcategory, and linesdeletedeCategory
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
sns.countplot(data=merged_prs, x='CommitsCategory', order=['Single commit', '2-5 commits', '6-10 commits', 'More than 10 commits'], palette='Set2', ax=axes[0, 0])
axes[0, 0].set_title('DevLLM: Distribution of Merged PRs by Number of Commits Categories')
axes[0, 0].set_xlabel('Commits Category')
axes[0, 0].set_ylabel('Number of Merged PRs')
axes[0, 0].tick_params(axis='x', rotation=45)
sns.countplot(data=merged_prs, x='ChangedFilesCategory', order=['Single file', '2-5 files', '6-10 files', 'More than 10 files'], palette='Set2', ax=axes[0, 1])
axes[0, 1].set_title('DevLLM: Distribution of Merged PRs by Changed Files Categories')
axes[0, 1].set_xlabel('Changed Files Category')
axes[0, 1].set_ylabel('Number of Merged PRs')
axes[0, 1].tick_params(axis='x', rotation=45)
sns.countplot(data=merged_prs, x='LinesAddedCategory', order=['Single line', '2-10 lines', '11-50 lines', 'More than 50 lines'], palette='Set2', ax=axes[1, 0])
axes[1, 0].set_title('DevLLM: Distribution of Merged PRs by Lines Added Categories')
axes[1, 0].set_xlabel('Lines Added Category')
axes[1, 0].set_ylabel('Number of Merged PRs')
axes[1, 0].tick_params(axis='x', rotation=45)
sns.countplot(data=merged_prs, x='LinesDeletedCategory', order=['Single line', '2-10 lines', '11-50 lines', 'More than 50 lines'], palette='Set2', ax=axes[1, 1])
axes[1, 1].set_title('DevLLM: Distribution of Merged PRs by Lines Deleted Categories')
axes[1, 1].set_xlabel('Lines Deleted Category')
axes[1, 1].set_ylabel('Number of Merged PRs')
axes[1, 1].tick_params(axis='x', rotation=45)
plt.tight_layout()
plt.show()


# correlation analysis
# select the numerical columns for correlation analysis
numerical_columns = ['Number_of_Commits', 'Changed_Files_Count', 'Lines_Added', 'Lines_Deleted', 'TimeToMergeHours', 'PRUpdateInterval']
correlation_matrix = merged_prs[numerical_columns].corr()
# print the correlation matrix
print("Correlation Matrix:\n", correlation_matrix)

# plot the correlation matrix
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Correlation Matrix of Merged PRs')
plt.show()


# now on all 3 states open merged closed prs


open_prs['CreatedAt'] = pd.to_datetime(open_prs['CreatedAt'])
open_prs['UpdatedAt'] = pd.to_datetime(open_prs['UpdatedAt'])

open_prs['PRUpdateInterval'] = (open_prs['UpdatedAt'] - open_prs['CreatedAt']).dt.total_seconds() / 3600


closed_prs['CreatedAt'] = pd.to_datetime(closed_prs['CreatedAt'])
closed_prs['UpdatedAt'] = pd.to_datetime(closed_prs['UpdatedAt'])
closed_prs['PRUpdateInterval'] = (closed_prs['UpdatedAt'] - closed_prs['CreatedAt']).dt.total_seconds() / 3600
closed_prs['ClosedAt'] = pd.to_datetime(closed_prs['ClosedAt'])
closed_prs['TimeToCloseHours'] = (closed_prs['ClosedAt'] - closed_prs['CreatedAt']).dt.total_seconds() / 3600


# Load the closed PR dataset
closed_reasons = pd.read_csv("closed_reasons_llm2.csv")
# Load open PR dataset
open_reasons = pd.read_csv("open_reasons_llm2.csv")
# Load merged PR dataset
merged_reasons = pd.read_csv("merged_reasons_llm2.csv")


print("Closed Reasons shape:", closed_reasons.shape)
print("Open Reasons shape:", open_reasons.shape)
print("Merged Reasons shape:", merged_reasons.shape)


def ensure_pr_url(url):
    """Ensure that the URL is in PR URL format (e.g., https://github.com/owner/repo/pull/123)."""
    if "/pull/" in url:
        return url
    elif "/issues/" in url:
        return url.replace("/issues/", "/pull/")
    else:
        return url


merged_reasons['primary_reason'].value_counts()


# show merged_reasons full line of comments for documentation primary_reason
documentation_reasons = merged_reasons[merged_reasons['primary_reason'] == 'DOCUMENTATION']
print("\nSample full comments for DOCUMENTATION primary_reason:")
for idx, row in documentation_reasons.head(3).iterrows():
    print(f"\nPR_URL: {row['PR_URL']}")
    print(f"Summary: {row['summary']}")


# show each primary_reason full summaries for 3 instances from merged reasons
for reason in merged_reasons['primary_reason'].unique():
    reason_subset = merged_reasons[merged_reasons['primary_reason'] == reason]
    print(f"\nPrimary Reason: {reason} | Total Merged PRs: {len(reason_subset)}")
    print("Sample Summaries:")
    print(reason_subset['summary'].head(3).to_string(index=False))

# show merged_reasons full line of comments for changes_requested primary_reason
changes_requested_reasons = merged_reasons[merged_reasons['primary_reason'] == 'CHANGES_REQUESTED']
print("\nSample full comments for CHANGES_REQUESTED primary_reason:")
for idx, row in changes_requested_reasons.head(3).iterrows():
    print(f"\nPR_URL: {row['PR_URL']}")
    print(f"Summary: {row['summary']}")



# show merged conflicts_reasons full line of comments for merge_conflict primary_reason
merge_conflict_reasons = merged_reasons[merged_reasons['primary_reason'] == 'MERGE_CONFLICT']
print("\nSample full comments for MERGE_CONFLICT primary_reason:")
for idx, row in merge_conflict_reasons.head(3).iterrows():
    print(f"\nPR_URL: {row['PR_URL']}")
    print(f"Summary: {row['summary']}")

open_reasons["primary_reason"].value_counts()

# show for open_reasons full line of comments for merge_conflict primary_reason
merge_conflict_open_reasons = open_reasons[open_reasons['primary_reason'] == 'MERGE_CONFLICT']
print("\nSample full comments for MERGE_CONFLICT primary_reason in open PRs:")
for idx, row in merge_conflict_open_reasons.head(3).iterrows():
    print(f"\nPR_URL: {row['PR_URL']}")
    print(f"Summary: {row['summary']}")


closed_reasons["primary_reason"].value_counts()

# show for closed_reasons full line of comments for merge_conflict primary_reason
merge_conflict_closed_reasons = closed_reasons[closed_reasons['primary_reason'] == 'MERGE_CONFLICT']
print("\nSample full comments for MERGE_CONFLICT primary_reason in closed PRs:")
for idx, row in merge_conflict_closed_reasons.head(10).iterrows():
    print(f"\nPR_URL: {row['PR_URL']}")
    print(f"Summary: {row['summary']}")

# plot horizantally the closed_reasons primary_reason counts
closed_reason_counts = closed_reasons['primary_reason'].value_counts()
plt.figure(figsize=(10,6))
sns.barplot(y=closed_reason_counts.index, x=closed_reason_counts.values, palette='Set2', orient='h')
plt.title('Closed Pull Requests by Primary Reason')
plt.xlabel('Number of Closed Pull Requests')
plt.ylabel('Primary Reason')
plt.show()

# plot horizantally the open_reasons primary_reason counts
open_reason_counts = open_reasons['primary_reason'].value_counts()
plt.figure(figsize=(10,6))
sns.barplot(y=open_reason_counts.index, x=open_reason_counts.values, palette='Set2', orient='h')
plt.title('Open Pull Requests by Primary Reason')
plt.xlabel('Number of Open Pull Requests')
plt.ylabel('Primary Reason')
plt.show()

#plot together side by side the open and closed primary_reason counts
fig, axes = plt.subplots(1, 2, figsize=(16, 6))     
sns.barplot(y=closed_reason_counts.index, x=closed_reason_counts.values, palette='Set2', orient='h', ax=axes[0])
axes[0].set_title('Closed Pull Requests by Primary Reason')
axes[0].set_xlabel('Number of Closed Pull Requests')
axes[0].set_ylabel('Primary Reason')        
sns.barplot(y=open_reason_counts.index, x=open_reason_counts.values, palette='Set2', orient='h', ax=axes[1])
axes[1].set_title('Open Pull Requests by Primary Reason')
axes[1].set_xlabel('Number of Open Pull Requests')
axes[1].set_ylabel('Primary Reason')
plt.tight_layout()
plt.show()


# Reasons on X label alphabetically and closed and open counts on Y label, 
reason_labels = sorted(list(set(closed_reason_counts.index).union(set(open_reason_counts.index))))
closed_counts = [closed_reason_counts.get(label, 0) for label in reason_labels]
open_counts = [open_reason_counts.get(label, 0) for label in reason_labels] 
x = range(len(reason_labels))
# color palette
colors = ['#8B0000', '#32CD32']  # brown red for closed, lime green for open
plt.figure(figsize=(12, 6))
plt.bar(x, closed_counts, width=0.4, label='Closed PRs', align='center', color=colors[0])
plt.bar([i + 0.4 for i in x], open_counts, width=0.4, label='Open PRs', align='center', color=colors[1])
plt.xlabel('Primary Reason')
plt.ylabel('Number of Pull Requests')
plt.title('DevGPT: Open vs Closed Pull Requests by Primary Reason')
plt.xticks([i + 0.2 for i in x], reason_labels, rotation=75)
plt.legend()
plt.tight_layout()
plt.show()

all_reasons = pd.concat([open_reasons, closed_reasons], ignore_index=True)


all_reasons["primary_reason"].value_counts()


closed_only = all_reasons[all_reasons["pr_state"] == "closed"]
closed_only["primary_reason"].value_counts()


closed_only[["PR_URL", "primary_reason", "summary"]].head(10)


for idx, row in all_reasons.iterrows():
    print("\n---", row["PR_URL"], "------------------")
    print(row["summary"])


df_llm.columns
df_llm.shape


# make primary reasons column for all open closed merged reasons, and , and add to df_llm dataset, and name it to final_dataset
final_dataset = df_llm.copy()
final_dataset = df_llm.merge(
    all_reasons[["PR_URL", "primary_reason", "summary"]],   
    left_on=final_dataset["URL"].apply(ensure_pr_url),
    right_on="PR_URL",
    how="left"
)
# a label column using corresponding values : open_prs, closed_prs, and merged_prs
final_dataset["subset_label"] = final_dataset["URL"].apply(ensure_pr_url).map(
    lambda url: "open_prs" if url in set(open_reasons["PR_URL"]) else
                "closed_prs" if url in set(closed_reasons["PR_URL"]) else
                "merged_prs" if url in set(merged_reasons["PR_URL"]) else
                "unknown"
)   

final_dataset.columns

#drop PR_URL key column
# final_dataset = final_dataset.drop(columns=["PR_URL", ])


final_dataset.shape

# save a csv named final_pr_analysis.csv
final_dataset.to_csv("final_pr_analysis.csv", index=False)

# a dataframe with all_reasons merged with df_llm on PR_URL and labeled columns Pr
df_reasons_merged = df_llm.merge(
    all_reasons,
    left_on=df_llm["URL"].apply(ensure_pr_url),
    right_on="PR_URL",
    how="left",
    suffixes=("", "_reason"),
)

# show closed prs with primary reasons
closed_prs_with_reasons = df_reasons_merged[df_reasons_merged["State"] == "closed"]
print("Total closed PRs with reasons:", closed_prs_with_reasons.shape[0])
print("Sample closed PRs with primary reasons from each category:")
print(closed_prs_with_reasons[['RepoName','URL','Title','primary_reason','summary']].head(100).to_string(index=False))
