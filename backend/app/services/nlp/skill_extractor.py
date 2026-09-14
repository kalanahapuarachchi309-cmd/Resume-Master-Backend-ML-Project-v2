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
    def extract_email(text: str) -> Optional[str]:
        """Extract primary candidate email address from resume text."""
        if not text:
            return None
        match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)
        return match.group(0).lower() if match else None

    @staticmethod
    def extract_phone(text: str) -> Optional[str]:
        """Extract phone number if present."""
        if not text:
            return None
        match = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
        return match.group(0).strip() if match else None

    @staticmethod
    def extract_experience_years(text: str) -> float:
        """Parse resume for professional work experience using regex, section filtering & merged intervals."""
        if not text:
            return 0.0

        # Pattern 1: Explicit statements ("5+ years of experience", "worked for 4 years")
        explicit_patterns = [
            r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:professional|industry|hands-on|relevant)?\s*experience",
            r"experience\s*:\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)",
            r"worked\s+(?:for\s+)?(\d+(?:\.\d+)?)\s*(?:years?|yrs?)",
            r"over\s+(\d+(?:\.\d+)?)\s*(?:years?|yrs?)(?:\s+of)?\s+experience",
        ]

        for pat in explicit_patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                try:
                    exp = float(match.group(1))
                    if 0.5 <= exp <= 30.0:
                        return round(exp, 1)
                except ValueError:
                    pass

        # Pattern 2: Extract date ranges with interval merging
        current_year = datetime.now().year
        
        # Split text into lines to exclude education sections from date calculation
        lines = text.split('\n')
        in_education_section = False
        work_lines = []
        for line in lines:
            line_clean = line.strip().lower()
            if any(h in line_clean for h in ["education", "academic", "degrees", "qualifications", "certifications"]):
                in_education_section = True
            elif any(h in line_clean for h in ["work experience", "experience", "employment", "professional experience", "career", "projects"]):
                in_education_section = False
            
            if not in_education_section:
                work_lines.append(line)
        
        target_text = "\n".join(work_lines) if work_lines else text

        # Find month/year or year-only date spans
        # Matches: 2018 - 2022, 01/2019 - Present, Jan 2020 to May 2023
        year_matches = re.findall(
            r"\b(20\d\d|19\d\d)\s*(?:-|–|to)\s*(20\d\d|present|current)\b",
            target_text,
            re.IGNORECASE
        )

        intervals = []
        for start_str, end_str in year_matches:
            try:
                start_y = int(start_str)
                end_y = current_year if end_str.lower() in ["present", "current"] else int(end_str)
                if 1980 <= start_y <= current_year and start_y <= end_y:
                    # Single year jobs count as at least 0.5 - 1.0 years
                    effective_end = max(end_y, start_y + 1)
                    # Limit ongoing single job duration to max 8 years if entry level / intern mentioned
                    if end_str.lower() in ["present", "current"] and any(w in target_text.lower() for w in ["entry level", "junior", "intern"]):
                        effective_end = min(effective_end, start_y + 3)
                    intervals.append((start_y, effective_end))
            except ValueError:
                pass

        if not intervals:
            # Check if any single recent graduation year exists
            return 0.0

        # Merge overlapping intervals to avoid double-counting parallel roles
        intervals.sort(key=lambda x: x[0])
        merged = []
        for start, end in intervals:
            if not merged or start > merged[-1][1]:
                merged.append([start, end])
            else:
                merged[-1][1] = max(merged[-1][1], end)

        total_years = sum(end - start for start, end in merged)
        return float(min(30.0, max(0.0, total_years)))

    @staticmethod
    