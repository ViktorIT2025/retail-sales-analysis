# Retail Sales Analysis

Retail sales analysis using Python and SQL to explore product performance, customer purchasing patterns, and monthly sales trends, with an interactive website.

**Live site:** https://viktorit2025.github.io/retail-sales-analysis/

## Data

[Retail Sales Dataset](https://www.kaggle.com/datasets/mohammadtalib786/retail-sales-dataset) from Kaggle: 1,000 transactions from January 1, 2023 to January 1, 2024, with customer age and gender, product category (Beauty, Clothing, Electronics), quantity, unit price and total amount. Each customer appears once.

## What's in the repo

| File | What it does |
|------|--------------|
| `retail_sales_analysis.ipynb` | Data validation, SQL (SQLite) and pandas checks of the headline totals, category performance, monthly trends, category-by-month heatmap, and a decomposition of revenue changes into transaction count and average purchase |
| `customer_patterns.ipynb` | Customer analysis by age group, gender, basket size, price tier and weekday, with statistical tests (Spearman, Kruskal-Wallis, chi-square) to check whether differences are real |
| `docs/` | The interactive website (published with GitHub Pages): sales overview, month comparison, customers and transactions |
| `analysis/outputs/` | Category and monthly summary tables exported from the notebook |

## Key findings

- Revenue was 456,000 across 1,000 transactions, split almost evenly between Electronics, Clothing and Beauty.
- Expensive items (300 or 500 per unit) were 40% of transactions but 88% of revenue.
- Age, gender and weekday differences were not statistically significant (all p-values above 0.2).
- One year of data with no repeat customers is not enough to study seasonality or customer loyalty.

## How to run

```bash
pip install -r requirements.txt
jupyter lab                 # open the notebooks
```

## Authors

- **Viktor Kliufinskyi** ([@ViktorIT2025](https://github.com/ViktorIT2025)): data validation, SQL, sales performance analysis, website
- **Diego Delgado** ([@diegodelg23](https://github.com/diegodelg23)): customer patterns analysis, website Customers tab
