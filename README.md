# CSC-790-Advanced-Software-Engineering Research


# Evaluating the Impact of LLM-Generated Commits on Developer Workflows

This project provides a data-driven framework to understand how Large Language Model (LLM)–generated commits influence real-world software development. We analyze merged, open, and closed pull requests (PRs) across multiple GitHub repositories to determine **when LLMs help developers** and **when they introduce friction**.

---

## 🔍 Research Questions
- **RQ1:** How do LLM commits help developers?
- **RQ2:** How do LLM commits *not* help developers?

These questions guide all metrics and analysis in this project.

---

## 📘 Datasets
We use two curated datasets and combine them into a single evaluation corpus:

### **1. DevGPT**
- 17,913 developer prompts  
- 11,751 ChatGPT responses  
- Linked artifacts: code, commits, issues, PRs, and discussions

### **2. DevLLM**
- 1,541 PRs from actively maintained GitHub repositories  
- 153 explicitly LLM-assisted PRs (ChatGPT, Copilot, Claude, Gemini, CodeLlama, etc.)

### **3. Aggregate Dataset**
- 420 PRs  
- 221 unique repositories  
- Metadata, reviews, comments, and CI results collected for each PR

---

## 🧠 Metrics

### **1. Time-to-Integration (TTI)**
Measures how long it takes a PR to merge, helping quantify whether LLM-generated code speeds up or slows down integration.

### **2. Code-Change Categorization (CCC)**
Classifies PRs into change categories: functionality, maintenance, non-functional, and other types of edits.

### **3. PR Primary Reason Metric (PPRM)**
A rule-based classifier that determines *why* each PR is open, stalled, or closed using:
- PR metadata  
- Reviewer decisions  
- Issue comments  
- CI check runs  

Produces interpretable categories such as:
`MERGE_CONFLICT`, `BLOCKED_DEP`, `CHANGES_REQUESTED`, `STALE`, and more.

### **4. Line-Change Pattern Metric (LCPM)**
Analyzes diff patterns (additions/deletions) to detect over-editing, hallucination-like behavior, or clean structured edits.

---

## 📊 Key Insights

### ✅ When LLM commits *help* developers
- Faster merges for documentation and small refactorings  
- Cleaner, more structured diffs  
- Reduced manual workload on repetitive tasks  

### ❌ When LLM commits *do not help*
- Slower merges for bug fixes and features  
- Higher CI failure rates  
- More reviewer-requested changes  
- Larger or noisier diffs indicating hallucinations  

---

## ⚙️ Workflow Summary

1. Fetch PR metadata, reviews, comments, and CI results via GitHub REST API  
2. Normalize and preprocess signals  
3. Apply four developer-centric metrics  
4. Compare LLM vs non-LLM PR behavior  
5. Interpret findings with respect to RQ1 and RQ2  

---


