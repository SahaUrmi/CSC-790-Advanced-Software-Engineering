#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Converted from Jupyter Notebook: aggregate.ipynb
Conversion Date: 2025-12-06T06:37:17.919Z
"""

import pandas as pd

# Load the labeled dataset
df_llm = pd.read_csv("combined_dataset.csv")  # Update this path to your dataset location

print("Dataset shape:", df_llm.shape)
df_llm.head()

df_llm.columns

# unique repos
unique_repos = df_llm['RepoName'].nunique()
print("Number of unique repositories:", unique_repos)
# print top 10 largest repos by RepoName
top_repos = df_llm['RepoName'].value_counts().head(10)
print("Top 10 largest repositories by number of PRs:")
print(top_repos)



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
plt.title('Distribution of Merged PRs by Time-to-Integration Categories')
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

# print noun followed by verb in the title second position
noun_verb_titles = merged_prs[merged_prs['Title'].str.contains('|'.join(set(noun_tokens)) + r'\s+' + '|'.join(set(verb_tokens)), case=False, na=False)]
print("Total merged PRs with noun followed by verb in the title:", noun_verb_titles.shape[0])
# show those prs titles with noun followed by verb
print("------"*15)
print("Merged PRs with noun followed by verb in the title:\n", noun_verb_titles[['RepoName', 'Title']].head(10))
print("------"*15)

# in these pairs only unique noun presented 
unique_noun_followed_by_verb = set()
for title in noun_verb_titles['Title']:
    words = title.split()
    for i in range(len(words) - 1):
        if words[i] in unique_noun_tokens and words[i+1] in unique_verb_tokens:
            unique_noun_followed_by_verb.add(words[i])
print("Unique noun tokens followed by verb in Titles:", unique_noun_followed_by_verb)
print("Total unique noun tokens followed by verb in Titles:", len(unique_noun_followed_by_verb))

# Total unique count of verb followed by noun in titles
unique_verb_followed_by_noun = set()
for title in noun_verb_titles['Title']:
    words = title.split()
    for i in range(len(words) - 1):
        if words[i] in unique_verb_tokens and words[i+1] in unique_noun_tokens:
            unique_verb_followed_by_noun.add(words[i])
print("Unique verb tokens followed by noun in Titles:", unique_verb_followed_by_noun)
print("Total unique verb tokens followed by noun in Titles:", len(unique_verb_followed_by_noun))
# most occuring pair of noun followed by verb
noun_verb_pairs = []
for title in noun_verb_titles['Title']:
    words = title.split()
    for i in range(len(words) - 1):
        if words[i] in unique_noun_tokens and words[i+1] in unique_verb_tokens:
            noun_verb_pairs.append((words[i], words[i+1]))
most_common_noun_verb_pairs = Counter(noun_verb_pairs).most_common(10)
print("Most common noun-verb pairs in titles:")
print(most_common_noun_verb_pairs)

# most occuring pair of verb followed by noun
verb_noun_pairs = []
for title in noun_verb_titles['Title']:
    words = title.split()
    for i in range(len(words) - 1):
        if words[i] in unique_verb_tokens and words[i+1] in unique_noun_tokens:
            verb_noun_pairs.append((words[i], words[i+1]))
most_common_verb_noun_pairs = Counter(verb_noun_pairs).most_common(10)
print("Most common verb-noun pairs in titles:")
print(most_common_verb_noun_pairs)

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
plt.title('Distribution of Merged PRs by Update Interval Categories')
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
plt.title('Distribution of Merged PRs by Number of Commits Categories')
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
plt.title('Distribution of Merged PRs by Changed Files Categories')
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
plt.title('Distribution of Merged PRs by Lines Added Categories')
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
plt.title('Distribution of Merged PRs by Lines Deleted Categories')
plt.xlabel('Lines Deleted Category')
plt.ylabel('Number of Merged PRs')
plt.xticks(rotation=45)
plt.show()


# #### General Analysis


# plot together in one figure side by side the committscategory, changedfilescategory, linesaddedcategory, and linesdeletedeCategory
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
sns.countplot(data=merged_prs, x='CommitsCategory', order=['Single commit', '2-5 commits', '6-10 commits', 'More than 10 commits'], palette='Set2', ax=axes[0, 0])
axes[0, 0].set_title('Distribution of Merged PRs by Number of Commits Categories')
axes[0, 0].set_xlabel('Commits Category')
axes[0, 0].set_ylabel('Number of Merged PRs')
axes[0, 0].tick_params(axis='x', rotation=45)
sns.countplot(data=merged_prs, x='ChangedFilesCategory', order=['Single file', '2-5 files', '6-10 files', 'More than 10 files'], palette='Set2', ax=axes[0, 1])
axes[0, 1].set_title('Distribution of Merged PRs by Changed Files Categories')
axes[0, 1].set_xlabel('Changed Files Category')
axes[0, 1].set_ylabel('Number of Merged PRs')
axes[0, 1].tick_params(axis='x', rotation=45)
sns.countplot(data=merged_prs, x='LinesAddedCategory', order=['Single line', '2-10 lines', '11-50 lines', 'More than 50 lines'], palette='Set2', ax=axes[1, 0])
axes[1, 0].set_title('Distribution of Merged PRs by Lines Added Categories')
axes[1, 0].set_xlabel('Lines Added Category')
axes[1, 0].set_ylabel('Number of Merged PRs')
axes[1, 0].tick_params(axis='x', rotation=45)
sns.countplot(data=merged_prs, x='LinesDeletedCategory', order=['Single line', '2-10 lines', '11-50 lines', 'More than 50 lines'], palette='Set2', ax=axes[1, 1])
axes[1, 1].set_title('Distribution of Merged PRs by Lines Deleted Categories')
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


# Calculate time to merge in hours
merged_prs['TimeToMergeHours'] = (merged_prs['MergedAt'] - merged_prs['CreatedAt']).dt.total_seconds() / 3600

# Distribution plot
plt.figure(figsize=(10, 6))
plt.hist(merged_prs['TimeToMergeHours'], bins=50, edgecolor='black')
plt.xlabel('Time to Merge (hours)')
plt.ylabel('Frequency')
plt.title('Distribution of Time to Merge for Merged PRs')
plt.show()

# Average time to merge by repository
avg_time_by_repo = merged_prs.groupby('RepoName')['TimeToMergeHours'].mean().sort_values(ascending=False)
print("Top 10 Repositories by Average Time to Merge:")
print(avg_time_by_repo.head(10))


merged_prs.columns

# time to merge by category ChangeType
avg_time_by_changetype = merged_prs.groupby('ChangeType')['TimeToMergeHours'].mean().sort_values(ascending=False)
print("Average Time to Merge by ChangeType:")
print(avg_time_by_changetype)

# plot the average time to merge by changetype as horizontal bar chart
plt.figure(figsize=(10, 6))
avg_time_by_changetype.plot(kind='barh')
plt.xlabel('Average Time to Merge (hours)')
plt.ylabel('ChangeType')
plt.title('Average Time to Merge by ChangeType')
plt.show()


# count of each changetype in merged_prs
changetype_counts = merged_prs['ChangeType'].value_counts()
print("ChangeType Counts:")
print(changetype_counts)

# plot the count of each changetype
plt.figure(figsize=(10, 6))
changetype_counts.plot(kind='barh')
plt.xlabel('Count')
plt.ylabel('ChangeType')
plt.title('Count of ChangeTypes in Merged PRs')
plt.show()


# create ChangeGroup column from ChangeType using the following mapping:
# Bug fix, Changed/Modified, Feature, Removed -> Functionality
# Dependencies, Optimization, Refactoring -> Maintenance
# Configuration changes, Documentation, Style and formatting, Tests -> Non-functional
# Other -> Other

def categorize_changegroup(row):
    changetype = row['ChangeType']
    if changetype in ['Bug fix', 'Changed/Modified', 'Feature', 'Removed']:
        return 'Functionality'
    elif changetype in ['Dependencies', 'Optimization', 'Refactoring']:
        return 'Maintenance'
    elif changetype in ['Configuration changes', 'Documentation', 'Style and formatting', 'Tests']:
        return 'Non-functional'
    else:
        return 'Other'

merged_prs['ChangeGroup'] = merged_prs.apply(categorize_changegroup, axis=1)

# count of each changegroup in merged_prs
changegroup_counts = merged_prs['ChangeGroup'].value_counts()
print("ChangeGroup Counts:")
print(changegroup_counts)

# plot the count of each changegroup
plt.figure(figsize=(10, 6))
changegroup_counts.plot(kind='barh')
plt.xlabel('Count')
plt.ylabel('ChangeGroup')
plt.title('Count of ChangeGroups in Merged PRs')
plt.show()


# average time to merge by changegroup
avg_time_by_changegroup = merged_prs.groupby('ChangeGroup')['TimeToMergeHours'].mean().sort_values(ascending=False)
print("Average Time to Merge by ChangeGroup:")
print(avg_time_by_changegroup)

# plot the average time to merge by changegroup as horizontal bar chart
plt.figure(figsize=(10, 6))
avg_time_by_changegroup.plot(kind='barh')
plt.xlabel('Average Time to Merge (hours)')
plt.ylabel('ChangeGroup')
plt.title('Average Time to Merge by ChangeGroup')
plt.show()


# put all the plots together
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
avg_time_by_changetype.plot(kind='barh', ax=axes[0, 0])
axes[0, 0].set_xlabel('Average Time to Merge (hours)')
axes[0, 0].set_ylabel('ChangeType')
axes[0, 0].set_title('Average Time to Merge by ChangeType')
changetype_counts.plot(kind='barh', ax=axes[0, 1])
axes[0, 1].set_xlabel('Count')
axes[0, 1].set_ylabel('ChangeType')
axes[0, 1].set_title('Count of ChangeTypes in Merged PRs')
avg_time_by_changegroup.plot(kind='barh', ax=axes[1, 0])
axes[1, 0].set_xlabel('Average Time to Merge (hours)')
axes[1, 0].set_ylabel('ChangeGroup')
axes[1, 0].set_title('Average Time to Merge by ChangeGroup')
changegroup_counts.plot(kind='barh', ax=axes[1, 1])
axes[1, 1].set_xlabel('Count')
axes[1, 1].set_ylabel('ChangeGroup')
axes[1, 1].set_title('Count of ChangeGroups in Merged PRs')
plt.tight_layout()
plt.show()


# #### Analysis on all (open closed merged ) PR


# calculate update interval for all prs
df_llm['UpdatedAt'] = pd.to_datetime(df_llm['UpdatedAt'])
df_llm['CreatedAt'] = pd.to_datetime(df_llm['CreatedAt'])
df_llm['PRUpdateInterval'] = (df_llm['UpdatedAt'] - df_llm['CreatedAt']).dt.total_seconds() / 3600


# create updateIntervalCategory for all prs
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

df_llm['UpdateIntervalCategory'] = df_llm.apply(categorize_update_interval, axis=1)

# plot the distribution of all prs by updateIntervalCategory
category_order = ['Direct merge', '0-2 hours', '2-4 hours', '4-8 hours', '8 hours - 1 day', 'half a week : 1-3 days', 'almost a week : 3-7 days', 'More than 7 days']
df_llm['UpdateIntervalCategory'] = pd.Categorical(df_llm['UpdateIntervalCategory'], categories=category_order, ordered=True)
plt.figure(figsize=(12,6))
sns.countplot(data=df_llm, x='UpdateIntervalCategory', order=category_order, palette='Set2')
plt.title('Distribution of All PRs by Update Interval Categories')
plt.xlabel('Update Interval Category')
plt.ylabel('Number of PRs')
plt.xticks(rotation=45)
plt.show()


# create ChangeGroup column from ChangeType for all prs
df_llm['ChangeGroup'] = df_llm.apply(categorize_changegroup, axis=1)

# count of each changegroup in all prs
changegroup_counts_all = df_llm['ChangeGroup'].value_counts()
print("ChangeGroup Counts (All PRs):")
print(changegroup_counts_all)

# plot the count of each changegroup
plt.figure(figsize=(10, 6))
changegroup_counts_all.plot(kind='barh')
plt.xlabel('Count')
plt.ylabel('ChangeGroup')
plt.title('Count of ChangeGroups in All PRs')
plt.show()


# average update interval by changegroup for all prs
avg_update_interval_by_changegroup = df_llm.groupby('ChangeGroup')['PRUpdateInterval'].mean().sort_values(ascending=False)
print("Average Update Interval by ChangeGroup (All PRs):")
print(avg_update_interval_by_changegroup)

# plot the average update interval by changegroup as horizontal bar chart
plt.figure(figsize=(10, 6))
avg_update_interval_by_changegroup.plot(kind='barh')
plt.xlabel('Average Update Interval (hours)')
plt.ylabel('ChangeGroup')
plt.title('Average Update Interval by ChangeGroup (All PRs)')
plt.show()


# count of each changetype in all prs
changetype_counts_all = df_llm['ChangeType'].value_counts()
print("ChangeType Counts (All PRs):")
print(changetype_counts_all)

# plot the count of each changetype
plt.figure(figsize=(10, 6))
changetype_counts_all.plot(kind='barh')
plt.xlabel('Count')
plt.ylabel('ChangeType')
plt.title('Count of ChangeTypes in All PRs')
plt.show()


# average update interval by changetype for all prs
avg_update_interval_by_changetype = df_llm.groupby('ChangeType')['PRUpdateInterval'].mean().sort_values(ascending=False)
print("Average Update Interval by ChangeType (All PRs):")
print(avg_update_interval_by_changetype)

# plot the average update interval by changetype as horizontal bar chart
plt.figure(figsize=(10, 6))
avg_update_interval_by_changetype.plot(kind='barh')
plt.xlabel('Average Update Interval (hours)')
plt.ylabel('ChangeType')
plt.title('Average Update Interval by ChangeType (All PRs)')
plt.show()


# plot all 4 plots together
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
changegroup_counts_all.plot(kind='barh', ax=axes[0, 0])
axes[0, 0].set_xlabel('Count')
axes[0, 0].set_ylabel('ChangeGroup')
axes[0, 0].set_title('Count of ChangeGroups in All PRs')
avg_update_interval_by_changegroup.plot(kind='barh', ax=axes[0, 1])
axes[0, 1].set_xlabel('Average Update Interval (hours)')
axes[0, 1].set_ylabel('ChangeGroup')
axes[0, 1].set_title('Average Update Interval by ChangeGroup (All PRs)')
changetype_counts_all.plot(kind='barh', ax=axes[1, 0])
axes[1, 0].set_xlabel('Count')
axes[1, 0].set_ylabel('ChangeType')
axes[1, 0].set_title('Count of ChangeTypes in All PRs')
avg_update_interval_by_changetype.plot(kind='barh', ax=axes[1, 1])
axes[1, 1].set_xlabel('Average Update Interval (hours)')
axes[1, 1].set_ylabel('ChangeType')
axes[1, 1].set_title('Average Update Interval by ChangeType (All PRs)')
plt.tight_layout()
plt.show()


# #### Comparing DevGPT and DevLLM


# Load DevGPT and DevLLM datasets if they're separate
# For now, assuming we can filter by 'ChatgptSharing' or similar column

# Example: If ChatgptSharing indicates DevGPT vs DevLLM
# devgpt_prs = df_llm[df_llm['ChatgptSharing'] == 'DevGPT']
# devllm_prs = df_llm[df_llm['ChatgptSharing'] == 'DevLLM']

# For demonstration, let's create synthetic split (adjust based on actual data)
# Here we'll just show the structure

# Compare average time to merge
# avg_time_devgpt = devgpt_prs.groupby('ChangeGroup')['TimeToMergeHours'].mean()
# avg_time_devllm = devllm_prs.groupby('ChangeGroup')['TimeToMergeHours'].mean()

# # Plot comparison
# comparison = pd.DataFrame({'DevGPT': avg_time_devgpt, 'DevLLM': avg_time_devllm})
# comparison.plot(kind='bar', figsize=(10, 6))
# plt.ylabel('Average Time to Merge (hours)')
# plt.title('Comparison of Time to Merge: DevGPT vs DevLLM')
# plt.show()


# # Reproducing Figure 3 like visualization (if we have separate datasets)


import matplotlib.pyplot as plt
import pandas as pd

# -------------------------------------------
# 1) Hard-coded Average Time to Merge by ChangeType
# -------------------------------------------
combined = pd.Series({
    "Removed": 0.138750,
    "Style and formatting": 0.890278,
    "Optimization": 32.154167,
    "Bug fix": 107.499640,
    "Documentation": 166.124701,
    "Changed/Modified": 167.601604,
    "Other": 179.290437,
    "Feature": 187.039812,
    "Refactoring": 206.824120,
    "Configuration changes": 230.612121,
    "Tests": 303.977500,
    "Dependencies": 923.733500
})

devgpt = pd.Series({
    "Removed": 0.138750,
    "Optimization": 32.154167,
    "Bug fix": 122.599336,
    "Feature": 204.981792,
    "Refactoring": 218.962288,
    "Changed/Modified": 233.202607,
    "Other": 234.923452,
    "Tests": 303.977500,
    "Documentation": 348.796111,
    "Configuration changes": 398.673380,
    "Dependencies": 923.733500
})

devllm = pd.Series({
    "Refactoring": 0.475278,
    "Style and formatting": 0.890278,
    "Bug fix": 20.676389,
    "Configuration changes": 28.938611,
    "Other": 49.480069,
    "Documentation": 56.521856,
    "Changed/Modified": 72.844599,
    "Feature": 86.564722
})

# -------------------------------------------
# 2) Align all ChangeTypes union into a DataFrame
# -------------------------------------------
df = pd.DataFrame({
    "Combined": combined,
    "DevGPT": devgpt,
    "DevLLM": devllm
})

# Fill missing categories with NaN (they will not plot)
df_sorted = df.sort_index()

# ---------------------------
# 3) Plot
# ---------------------------
plt.figure(figsize=(12, 6))

plt.plot(df_sorted.index, df_sorted["Combined"], marker='o', label="Combined")
plt.plot(df_sorted.index, df_sorted["DevGPT"], marker='o', label="DevGPT")
plt.plot(df_sorted.index, df_sorted["DevLLM"], marker='o', label="DevLLM")

plt.xticks(rotation=45, ha='right')
plt.ylabel("Average Time to Merge (hours)")
plt.title("Average Time to Merge by ChangeType (Across Datasets)")
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()




import matplotlib.pyplot as plt
import numpy as np

# ==========================
# 1) ChangeGroup totals
# ==========================

combined = {
    "Functionality": 150,
    "Maintenance": 26,
    "Non-functional": 57,
    "Other": 40
}

devgpt = {
    "Functionality": 122,
    "Maintenance": 25,
    "Non-functional": 26,
    "Other": 28
}

devllm = {
    "Functionality": 28,
    "Maintenance": 1,
    "Non-functional": 31,
    "Other": 12
}

# ==========================
# 2) Prepare data for plotting
# ==========================

categories = list(combined.keys())
x = np.arange(len(categories))
width = 0.25

combined_vals = [combined[c] for c in categories]
devgpt_vals = [devgpt[c] for c in categories]
devllm_vals = [devllm[c] for c in categories]

# ==========================
# 3) Plot
# ==========================
# verify total devgpt and devllm each category sum to be combined category
for i, cat in enumerate(categories):
    total = devgpt_vals[i] + devllm_vals[i]
    combined_val = combined_vals[i]
    print(f"Category: {cat} | Combined: {combined_val} | DevGPT + DevLLM: {total} | Match: {combined_val == total}")    


# only plot combined but each category of combined should be sum of devgpt and devllm so with two colors stacked
plt.figure(figsize=(10, 6))
plt.bar(x, devgpt_vals, width, label='DevGPT', color="#9a88e1")
plt.bar(x, devllm_vals, width, bottom=devgpt_vals, label='DevLLM', color="#db9cd2")   
plt.xticks(x, categories, rotation=45, ha='right')
plt.ylabel('Number of PRs')
plt.title('PRs by ChangeGroup and Dataset (Stacked)')
plt.legend()
plt.tight_layout()
plt.show()




import matplotlib.pyplot as plt
import numpy as np

# ============================================================
# 1) Subcategory breakdown data
# ============================================================

combined = {
    "Functionality": {"Bug fix": 27, "Changed/Modified": 22, "Feature": 99, "Removed": 2},
    "Maintenance": {"Dependencies": 5, "Optimization": 3, "Refactoring": 18},
    "Non-functional": {"Configuration changes": 11, "Documentation": 40, "Style and formatting": 1, "Tests": 5},
    "Other": {"Other": 40}
}

devgpt = {
    "Functionality": {"Bug fix": 23, "Changed/Modified": 13, "Feature": 84, "Removed": 2},
    "Maintenance": {"Dependencies": 5, "Optimization": 3, "Refactoring": 17},
    "Non-functional": {"Configuration changes": 6, "Documentation": 15, "Tests": 5},
    "Other": {"Other": 28}
}

devllm = {
    "Functionality": {"Bug fix": 4, "Changed/Modified": 9, "Feature": 15},
    "Maintenance": {"Refactoring": 1},
    "Non-functional": {"Configuration changes": 5, "Documentation": 25, "Style and formatting": 1},
    "Other": {"Other": 12}
}

datasets = {"Combined": combined, "DevGPT": devgpt, "DevLLM": devllm}

# ============================================================
# 2) Prepare plotting structure
# ============================================================

groups = ["Functionality", "Maintenance", "Non-functional", "Other"]
x = np.arange(len(groups))
width = 0.22

plt.figure(figsize=(14, 7))

# Colors for repeated subcategories across datasets
color_map = {
    "Bug fix": "#1f77b4",
    "Changed/Modified": "#ff7f0e",
    "Feature": "#2ca02c",
    "Removed": "#d62728",
    "Refactoring": "#9467bd",
    "Dependencies": "#8c564b",
    "Optimization": "#e377c2",
    "Configuration changes": "#7f7f7f",
    "Documentation": "#bcbd22",
    "Style and formatting": "#17becf",
    "Tests": "#aec7e8",
    "Other": "#c49c94"
}

# ============================================================
# 3) Plot datasets as grouped stacked bars
# ============================================================

offsets = [-width, 0, width]   # Combined, DevGPT, DevLLM

for (dataset_name, ds), offset in zip(datasets.items(), offsets):
    bottoms = np.zeros(len(groups))
    
    for subgroup in set(k for g in groups for k in ds[g].keys()):
        values = [ds[g].get(subgroup, 0) for g in groups]
        plt.bar(
            x + offset,
            values,
            width,
            bottom=bottoms,
            label=f"{dataset_name} - {subgroup}" if dataset_name == "Combined" else "",
            color=color_map.get(subgroup, None)
        )
        bottoms += np.array(values)

# ============================================================
# 4) Formatting
# ============================================================

plt.xticks(x, groups, fontsize=10)
plt.ylabel("Count")
plt.title("ChangeGroup + Subcategory Breakdown Across Datasets\n(Stacked Subcategories, Grouped by Dataset)", fontsize=14)
plt.grid(axis='y', alpha=0.3)

# Show unique legends only once
handles, labels = plt.gca().get_legend_handles_labels()
unique = dict(zip(labels, handles))
plt.legend(unique.values(), unique.keys(), bbox_to_anchor=(1.02, 1), loc="upper left")

plt.tight_layout()
plt.show()
