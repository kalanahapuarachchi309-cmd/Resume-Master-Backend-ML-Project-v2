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

    }
