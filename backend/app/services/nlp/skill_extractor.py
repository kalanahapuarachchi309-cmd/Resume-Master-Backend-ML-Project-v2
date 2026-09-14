"""Skill, Experience, and Education Extractor with Normalization (Mahen & Team)."""
import re
from datetime import datetime
from typing import List, Optional, Tuple

# Technical skill taxonomy with canonical mappings
SKILL_ALIASES = {
    # Languages
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "python": "Python",
    "py": "Python",
    "java": "Java",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "golang": "Go",
    "go": "Go",
    "rust": "Rust",
    "php": "PHP",
    "ruby": "Ruby",
    "swift": "Swift",
    "kotlin": "Kotlin",
    
    # Frameworks & Libraries
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "angular": "Angular",
    "vue": "Vue",
    "vue.js": "Vue",
    "vuejs": "Vue",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express",
    "express.js": "Express",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "spring": "Spring Boot",
    "spring boot": "Spring Boot",
    "laravel": "Laravel",
    "dotnet": ".NET",
    ".net": ".NET",

    # Databases
    "sql": "SQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "elasticsearch": "Elasticsearch",
    "sqlite": "SQLite",
    "oracle": "Oracle",

    # Cloud & DevOps
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "google cloud": "GCP",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "linux": "Linux",
    "git": "Git",
    "github": "Git",
    "gitlab": "Git",
    "jenkins": "Jenkins",

    # AI / ML / Data
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "computer vision": "Computer Vision",
    "cv": "Computer Vision",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "scikit-learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "power bi": "Power BI",
    "tableau": "Tableau",
    "data analysis": "Data Analysis",

    # Web & Architecture
    "html": "HTML",
    "html5": "HTML",
    "css": "CSS",
    "css3": "CSS",
    "tailwind": "Tailwind CSS",
    "tailwind css": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "rest": "REST API",
    "rest api": "REST API",
    "restful": "REST API",
    "graphql": "GraphQL",
    "microservices": "Microservices",
    "selenium": "Selenium",
    "pytest": "Pytest",
}


class SkillExtractor:
    """Extracts normalized technical skills, experience duration, and degrees."""

    @staticmethod
    def extract_skills(text: str) -> List[str]:
        """Match and normalize programming languages, frameworks, and tools."""
        if not text:
            return []

        text_lower = f" {text.lower()} "
        found_skills = set()

        # Sort alias keys by length descending to match multi-word phrases first
        sorted_aliases = sorted(SKILL_ALIASES.keys(), key=lambda x: len(x), reverse=True)

        for alias in sorted_aliases:
            pattern = rf"(?:\b|\s){re.escape(alias)}(?:\b|\s|[,\.;])"
            if re.search(pattern, text_lower):
                canonical = SKILL_ALIASES[alias]
                found_skills.add(canonical)

        return sorted(list(found_skills))

    @staticmethod
    