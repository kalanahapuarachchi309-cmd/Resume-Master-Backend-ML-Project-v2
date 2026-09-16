"""Complete Machine Learning Training, Model Evaluation, and Artifact Serialization Pipeline.

Authored for: Machine Learning Module Group Project
Author / Lead: Hiruna (ML Engineer) & Kalana (Backend Lead)
Models Compared: Logistic Regression, Support Vector Machine (SVM), Random Forest Classifier
Exports:
  - backend/app/ml/model.pkl
  - backend/app/ml/vectorizer.pkl
  - ml_pipeline/EVALUATION_REPORT.md
"""

import os
import sys
import pickle
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

# ---------------------------------------------------------
# 1. CREDIBLE DATASET GENERATION / CURATION
# ---------------------------------------------------------

JOB_PROFILES = [
    {
        "title": "Senior Python Backend Developer",
        "description": "Looking for Senior Python Developer with deep experience in FastAPI, PostgreSQL, Docker, Redis, and microservices architecture. Minimum 4 years experience required with Bachelor degree.",
        "required_skills": ["python", "fastapi", "postgresql", "docker", "redis", "rest api"],
        "required_exp": 4.0,
        "required_edu": 2,  # Bachelor
    },
    {
        "title": "Frontend React Developer",
        "description": "Seeking Frontend React Developer proficient in TypeScript, Tailwind CSS, Redux, React Hooks, and responsive design. 2+ years of professional web development experience required.",
        "required_skills": ["react", "javascript", "typescript", "tailwind css", "html", "css"],
        "required_exp": 2.0,
        "required_edu": 2,
    },
    {
        "title": "Machine Learning & NLP Engineer",
        "description": "Hiring Machine Learning Engineer to build NLP and computer vision pipelines using Python, PyTorch, Scikit-Learn, Pandas, NumPy, and Docker. Master or Bachelor degree required with 3+ years experience.",
        "required_skills": ["python", "machine learning", "nlp", "pytorch", "scikit-learn", "pandas", "numpy"],
        "required_exp": 3.0,
        "required_edu": 2,
    },
    {
        "title": "DevOps & Cloud Infrastructure Engineer",
        "description": "Looking for DevOps Cloud Engineer with expertise in AWS, Docker, Kubernetes, CI/CD pipelines, Terraform, and Linux server administration. 3+ years experience required.",
        "required_skills": ["aws", "docker", "kubernetes", "ci/cd", "terraform", "linux"],
        "required_exp": 3.0,
        "required_edu": 2,
    },
    {
        "title": "Full Stack Software Engineer",
        "description": "Full Stack developer needed to build modern web applications using Python, FastAPI, React, PostgreSQL, Docker, and Git. 2.5+ years experience required.",
        "required_skills": ["python", "react", "fastapi", "postgresql", "docker", "git"],
        "required_exp": 2.5,
        "required_edu": 2,
    },
    {
        "title": "Data Analyst & Business Intelligence",
        "description": "Seeking Data Analyst skilled in SQL, Python, Tableau, Power BI, Excel, and Data Visualization. 2 years experience required.",
        "required_skills": ["sql", "python", "tableau", "power bi", "data analysis"],
        "required_exp": 2.0,
        "required_edu": 2,
    },
    {
        "title": "QA Automation Test Engineer",
        "description": "Looking for QA Automation Engineer with experience in Python, Selenium, Pytest, CI/CD, and API testing. 2+ years experience required.",
        "required_skills": ["python", "selenium", "pytest", "ci/cd", "rest api"],
        "required_exp": 2.0,
        "required_edu": 2,
    }
]

NON_TECH_PROFILES = [
    {
        "text": "Certified Public Accountant with 6 years experience in auditing, financial reporting, corporate tax, ledger reconciliation, QuickBooks, and payroll management. Bachelor in Accounting.",
        "skills": ["accounting", "financial reporting", "auditing", "taxation"],
        "exp": 6.0,
        "edu": 2,
    },
    {
        "text": "Senior Sales Executive and Business Development Manager with 5 years experience in B2B client acquisition, CRM pipeline, lead generation, and enterprise contract negotiations.",
        "skills": ["sales", "negotiation", "b2b", "crm"],
        "exp": 5.0,
        "edu": 1,
    },
    {
        "text": "Human Resources Coordinator experienced in talent acquisition, employee onboarding, benefits administration, labor compliance, and HR payroll software. 3 years experience.",
        "skills": ["human resources", "recruitment", "onboarding", "compliance"],
        "exp": 3.0,
        "edu": 2,
    },
    {
        "text": "Executive Chef and Kitchen Manager with 8 years culinary experience in luxury hospitality, menu planning, food safety, inventory control, and culinary team leadership.",
        "skills": ["culinary", "inventory", "food safety", "hospitality"],
        "exp": 8.0,
        "edu": 1,
    }
]


def build_credible_dataset(samples_per_role: int = 300) -> pd.DataFrame:
    """Construct a comprehensive dataset of realistic candidate resumes paired against jobs."""
    np.random.seed(42)
    rows = []

    for job in JOB_PROFILES:
        req_skills = job["required_skills"]
        req_exp = job["required_exp"]
        req_edu = job["required_edu"]

        for _ in range(samples_per_role):
            scenario = np.random.choice(
                ["perfect_match", "high_match", "moderate_match", "low_match", "mismatch"],
                p=[0.20, 0.30, 0.25, 0.15, 0.10]
            )

            if scenario == "perfect_match":
                # Candidate has 100% of required skills, meets or slightly exceeds experience
                cand_skills = list(req_skills) + ["git", "linux", "agile"]
                # Experience can be slightly below (-0.5) to well above (+4.0)
                cand_exp = round(max(0.5, req_exp + np.random.uniform(-0.5, 4.0)), 1)
                cand_edu = np.random.choice([2, 3, 4], p=[0.6, 0.3, 0.1])
                resume_text = f"Accomplished {job['title']} specialist offering complete technical proficiency in {', '.join(cand_skills)}. Successfully architected enterprise systems with {cand_exp} years of industry experience."
                label = 1

            elif scenario == "high_match":
                # Candidate has 80-95% of skills
                num_skills = max(2, len(req_skills) - 1)
                cand_skills = list(np.random.choice(req_skills, size=num_skills, replace=False))
                cand_skills += ["git", "docker", "agile"]
                cand_exp = round(max(0.5, req_exp + np.random.uniform(-1.0, 3.0)), 1)
                cand_edu = np.random.choice([2, 3, 4], p=[0.7, 0.25, 0.05])
                resume_text = f"Professional {job['title']} with strong domain expertise in {', '.join(cand_skills)}. Proven track record with {cand_exp} years in software engineering and cloud infrastructure."
                label = 1 if (cand_exp >= req_exp - 1.0) else (1 if num_skills >= len(req_skills) - 1 else 0)

            elif scenario == "moderate_match":
                # Candidate has 50-75% of skills
                min_sk = max(2, int(len(req_skills) * 0.5))
                max_sk = max(min_sk + 1, int(len(req_skills) * 0.8))
                num_skills = min(len(req_skills), np.random.randint(min_sk, max_sk + 1))
                cand_skills = list(np.random.choice(req_skills, size=num_skills, replace=False))
                cand_exp = round(max(0.5, req_exp + np.random.uniform(-1.0, 3.0)), 1)
                cand_edu = np.random.choice([1, 2, 3], p=[0.2, 0.7, 0.1])
                resume_text = f"Mid-level developer familiar with {', '.join(cand_skills)}. {cand_exp} years background working with modern development stacks and collaborative agile sprints."
                label = 1 if (num_skills >= len(req_skills) * 0.5 and cand_exp >= req_exp - 0.5) else 0

            elif scenario == "low_match":
                # Candidate has only 1-2 required skills
                num_skills = min(2, len(req_skills))
                cand_skills = list(np.random.choice(req_skills, size=num_skills, replace=False))
                cand_skills += ["html", "css", "photoshop", "ms office"]
                cand_exp = round(np.random.uniform(0.5, 2.0), 1)
                cand_edu = np.random.choice([0, 1, 2], p=[0.3, 0.5, 0.2])
                resume_text = f"Junior technologist with foundational exposure to {', '.join(cand_skills)}. Total experience {cand_exp} years with basic technical capabilities."
                label = 0

            else:  # mismatch
                non_tech = np.random.choice(NON_TECH_PROFILES)
                cand_skills = non_tech["skills"]
                cand_exp = non_tech["exp"]
                cand_edu = non_tech["edu"]
                resume_text = non_tech["text"]
                label = 0

            rows.append({
                "job_title": job["title"],
                "job_description": job["description"],
                "required_skills": req_skills,
                "required_exp": req_exp,
                "required_edu": req_edu,
                "resume_text": resume_text,
                "candidate_skills": cand_skills,
                "candidate_exp": cand_exp,
                "candidate_edu": cand_edu,
                "match_label": label,
            })

    return pd.DataFrame(rows)


# ---------------------------------------------------------
# 2. FEATURE EXTRACTION PIPELINE (MANDATORY 6-7 TECHNIQUES)
# ---------------------------------------------------------

def extract_features_for_dataset(df: pd.DataFrame, vectorizer: TfidfVectorizer, is_training: bool = True) -> np.ndarray:
    """Extract identical 7 numerical features across all resume-job pairs."""
    features_list = []

    # Prepare texts for TF-IDF
    corpus_pairs = df["resume_text"].tolist()

    if is_training:
        # Fit vectorizer only on training resume corpus + job descriptions
        all_texts = df["resume_text"].tolist() + df["job_description"].tolist()
        vectorizer.fit(all_texts)

    for _, row in df.iterrows():
        # 1. TF-IDF Semantic Text Similarity
        vec_resume = vectorizer.transform([row["resume_text"]])
        vec_job = vectorizer.transform([row["job_description"]])
        tfidf_sim = float(cosine_similarity(vec_resume, vec_job)[0][0])

        # 2. Skill Overlap Ratio (Jaccard-like intersection)
        c_skills = set(s.lower().strip() for s in row["candidate_skills"])
        r_skills = set(s.lower().strip() for s in row["required_skills"])
        matched = c_skills.intersection(r_skills)
        skill_overlap = len(matched) / len(r_skills) if r_skills else 1.0

        # 3. Total Matched Skill Count
        skill_count = len(matched)

        # 4. Missing Skill Ratio
        missing_skills = r_skills - c_skills
        missing_ratio = len(missing_skills) / len(r_skills) if r_skills else 0.0

        # 5. Experience Delta (Clipped to [-3, +3])
        cand_exp = row["candidate_exp"] if pd.notnull(row["candidate_exp"]) else 0.0
        req_exp = row["required_exp"] if pd.notnull(row["required_exp"]) else 0.0
        exp_delta = float(np.clip(cand_exp - req_exp, -3.0, 3.0))

        # 6. Experience Fit Binary (1 if candidate meets or exceeds required years)
        exp_fit = 1.0 if cand_exp >= req_exp else 0.0

        # 7. Education Level Ordinal (0 to 4)
        cand_edu = float(row["candidate_edu"]) if pd.notnull(row["candidate_edu"]) else 0.0

        features_list.append([
            tfidf_sim,
            skill_overlap,
            skill_count,
            missing_ratio,
            exp_delta,
            exp_fit,
            cand_edu,
        ])

    return np.array(features_list)


# ---------------------------------------------------------
# 3. MAIN TRAINING, EVALUATION & EXPORT ROUTINE
# ---------------------------------------------------------

def main():
    print("=" * 70)
    print("🚀 TRAINING & EVALUATION PIPELINE FOR RESUME SCREENING ML MODEL")
    print("=" * 70)

    # 1. Dataset Generation
    df = build_credible_dataset(samples_per_role=240)
    total_samples = len(df)
    positives = int(df["match_label"].sum())
    negatives = total_samples - positives

    print(f"✓ Generated Dataset: {total_samples} samples")
    print(f"  • Suitable Matches (Class 1): {positives} ({positives / total_samples * 100:.1f}%)")
    print(f"  • Unsuitable Matches (Class 0): {negatives} ({negatives / total_samples * 100:.1f}%)")

    # 2. Train / Test Split BEFORE feature vectorization (Prevents Data Leakage!)
    train_df, test_df = train_test_split(df, test_size=0.20, random_state=42, stratify=df["match_label"])
    print(f"✓ Split: {len(train_df)} Training pairs (80%) | {len(test_df)} Testing pairs (20%)")

    # 3. Global TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(max_features=500, stop_words="english", ngram_range=(1, 2))

    # 4. Feature Extraction
    print("✓ Extracting 7 engineered features...")
    X_train = extract_features_for_dataset(train_df, vectorizer, is_training=True)
    y_train = train_df["match_label"].values

    X_test = extract_features_for_dataset(test_df, vectorizer, is_training=False)
    y_test = test_df["match_label"].values

    # 5. Model Candidate Evaluation
    models = {
        "Random Forest Classifier": RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42),
        "Support Vector Machine (SVM)": SVC(probability=True, kernel="linear", random_state=42),
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    }

    results = {}
    best_model_name = None
    best_f1 = -1.0
    best_model = None

    print("\n" + "=" * 70)
    print(f"{'Model Name':<30} | {'Accuracy':<9} | {'Precision':<9} | {'Recall':<9} | {'F1-Score':<9} | {'ROC-AUC':<9}")
    print("-" * 70)

    for name, clf in models.items():
        # Train
        clf.fit(X_train, y_train)

        # Predict
        y_pred = clf.predict(X_test)
        y_proba = clf.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        auc = roc_auc_score(y_test, y_proba)
        cm = confusion_matrix(y_test, y_pred)

        results[name] = {
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "roc_auc": auc,
            "confusion_matrix": cm,
            "model": clf,
        }

        print(f"{name:<30} | {acc * 100:6.2f}%   | {prec * 100:6.2f}%   | {rec * 100:6.2f}%   | {f1 * 100:6.2f}%   | {auc:7.4f}")

        # Favor Random Forest if scores are equal
        if f1 > best_f1 or (f1 == best_f1 and "Random Forest" in name):
            best_f1 = f1
            best_model_name = name
            best_model = clf

    print("=" * 70)
    print(f"🏆 SELECTED BEST MODEL: {best_model_name} (F1-Score: {best_f1 * 100:.2f}%)")

    # 6. Save Artifacts for Backend
    export_dir = os.path.join(os.path.dirname(__file__), "..", "backend", "app", "ml")
    os.makedirs(export_dir, exist_ok=True)

    model_path = os.path.join(export_dir, "model.pkl")
    vectorizer_path = os.path.join(export_dir, "vectorizer.pkl")

    with open(model_path, "wb") as f:
        pickle.dump(best_model, f)
    with open(vectorizer_path, "wb") as f:
        pickle.dump(vectorizer, f)

    print(f"✓ Model successfully serialized: {os.path.abspath(model_path)}")
    print(f"✓ Vectorizer successfully serialized: {os.path.abspath(vectorizer_path)}")

    # 7. Generate EVALUATION_REPORT.md for Viva Voce & Academic Report
    report_path = os.path.join(os.path.dirname(__file__), "EVALUATION_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"""# Machine Learning Model Evaluation Report

**Project:** AI Resume/CV Screening & Job Matching System  
**Prepared by:** Hiruna (ML Engineer) & Backend Team  
**Evaluation Date:** {pd.Timestamp.now().strftime('%Y-%m-%d')}  
**Target Variable:** `match_label` (1 = Suitable Match, 0 = Unsuitable Match)  

---

## 1. Dataset Characteristics & Summary

- **Total Samples:** {total_samples} resume-to-job matching pairs
- **Class Distribution:**
  - Class 1 (Suitable Match): {positives} ({positives / total_samples * 100:.1f}%)
  - Class 0 (Unsuitable Match): {negatives} ({negatives / total_samples * 100:.1f}%)
- **Data Splitting:** 80% Train ({len(train_df)} pairs) / 20% Test ({len(test_df)} pairs) with stratified split to prevent data leakage.

---

## 2. Mandatory Feature Engineering Techniques (7 Features)

1. **TF-IDF Semantic Similarity:** Fitted on training text corpus; cosine similarity computed between candidate resume and job vacancy.
2. **Skill Overlap Ratio:** Jaccard-like intersection ratio: $|\\text{{Candidate Skills}} \\cap \\text{{Required Skills}}| / |\\text{{Required Skills}}|$.
3. **Skill Count:** Total count of overlapping required skills.
4. **Missing Skill Ratio:** Proportion of mandatory skills absent: $|\\text{{Missing Skills}}| / |\\text{{Required Skills}}|$.
5. **Experience Delta:** Candidate years minus required years, bounded within $[-3.0, +3.0]$.
6. **Experience Fit Binary:** Indicator variable (1 if candidate meets/exceeds requirement, 0 otherwise).
7. **Education Level Ordinal Encoding:** None=0, Diploma=1, Bachelor=2, Master=3, PhD=4.

---

## 3. Comparative Model Evaluation Results

| Model Name | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
""")
        for name, metrics in results.items():
            f.write(f"| **{name}** | {metrics['accuracy'] * 100:.2f}% | {metrics['precision'] * 100:.2f}% | {metrics['recall'] * 100:.2f}% | **{metrics['f1'] * 100:.2f}%** | {metrics['roc_auc']:.4f} |\n")

        f.write(f"""
---

## 4. Winning Model Selection

The **{best_model_name}** was selected for production inference because it achieved the highest **F1-Score of {best_f1 * 100:.2f}%**. In recruitment screening, F1-score is the optimal selection metric because it balances false positives (shortlisting unqualified candidates) and false negatives (rejecting qualified talent).

The serialized model is stored at `backend/app/ml/model.pkl` and directly integrated with the FastAPI ranking engine.
""")

    print(f"✓ Viva report generated: {os.path.abspath(report_path)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
