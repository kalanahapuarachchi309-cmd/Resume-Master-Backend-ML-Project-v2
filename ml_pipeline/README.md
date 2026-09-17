# Machine Learning Training & Evaluation Pipeline

This module manages the offline Machine Learning lifecycle for candidate evaluation, including synthetic and real dataset generation, feature engineering, multi-model benchmarking, and artifact serialization.

---

## 📂 ML Pipeline Structure

```text
ml_pipeline/
├── train_and_evaluate.py       # Dataset generation, model training & cross-validation script
├── EVALUATION_REPORT.md        # Accuracy, Precision, Recall, F1 & Confusion Matrix report
└── README.md                   # Pipeline documentation
```

---

## ⚙️ Execution

```bash
python train_and_evaluate.py
```
This script evaluates candidate algorithms (Random Forest, Decision Tree, Logistic Regression), serializes the champion model artifact (`model.pkl`) and TF-IDF vectorizer (`vectorizer.pkl`), and outputs benchmarking metrics.
