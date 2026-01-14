"""
Concept taxonomy for NCDPI Mathematics.
Hierarchical structure of mathematical concepts with prerequisites.
"""

NCDPI_MATH_CONCEPTS = [
    # Grade 3-5: Foundational Concepts
    {
        "concept_id": "number.place-value",
        "name": "Place Value",
        "description": "Understanding the value of digits based on their position",
        "subject": "mathematics",
        "grade_level_min": 3,
        "grade_level_max": 5,
        "exam_standard": "NCDPI",
        "parent_concept_id": None,
        "prerequisite_concept_ids": [],
    },
    {
        "concept_id": "number.addition",
        "name": "Addition",
        "description": "Adding whole numbers with and without regrouping",
        "subject": "mathematics",
        "grade_level_min": 3,
        "grade_level_max": 5,
        "exam_standard": "NCDPI",
        "parent_concept_id": "number.place-value",
        "prerequisite_concept_ids": ["number.place-value"],
    },
    {
        "concept_id": "number.subtraction",
        "name": "Subtraction",
        "description": "Subtracting whole numbers with and without regrouping",
        "subject": "mathematics",
        "grade_level_min": 3,
        "grade_level_max": 5,
        "exam_standard": "NCDPI",
        "parent_concept_id": "number.place-value",
        "prerequisite_concept_ids": ["number.place-value"],
    },
    {
        "concept_id": "number.multiplication",
        "name": "Multiplication",
        "description": "Multiplying whole numbers and understanding multiplication as repeated addition",
        "subject": "mathematics",
        "grade_level_min": 3,
        "grade_level_max": 5,
        "exam_standard": "NCDPI",
        "parent_concept_id": None,
        "prerequisite_concept_ids": ["number.addition"],
    },
    {
        "concept_id": "number.division",
        "name": "Division",
        "description": "Dividing whole numbers and understanding division as inverse of multiplication",
        "subject": "mathematics",
        "grade_level_min": 3,
        "grade_level_max": 5,
        "exam_standard": "NCDPI",
        "parent_concept_id": None,
        "prerequisite_concept_ids": ["number.multiplication"],
    },
    
    # Fractions
    {
        "concept_id": "fractions.basics",
        "name": "Fraction Basics",
        "description": "Understanding fractions as parts of a whole",
        "subject": "mathematics",
        "grade_level_min": 3,
        "grade_level_max": 5,
        "exam_standard": "NCDPI",
        "parent_concept_id": None,
        "prerequisite_concept_ids": ["number.division"],
    },
    {
        "concept_id": "fractions.equivalent",
        "name": "Equivalent Fractions",
        "description": "Identifying and creating equivalent fractions",
        "subject": "mathematics",
        "grade_level_min": 4,
        "grade_level_max": 6,
        "exam_standard": "NCDPI",
        "parent_concept_id": "fractions.basics",
        "prerequisite_concept_ids": ["fractions.basics", "number.multiplication"],
    },
    {
        "concept_id": "fractions.common-denominators",
        "name": "Common Denominators",
        "description": "Finding common denominators for fraction operations",
        "subject": "mathematics",
        "grade_level_min": 4,
        "grade_level_max": 6,
        "exam_standard": "NCDPI",
        "parent_concept_id": "fractions.equivalent",
        "prerequisite_concept_ids": ["fractions.equivalent"],
    },
    {
        "concept_id": "fractions.adding",
        "name": "Adding Fractions",
        "description": "Adding fractions with like and unlike denominators",
        "subject": "mathematics",
        "grade_level_min": 4,
        "grade_level_max": 6,
        "exam_standard": "NCDPI",
        "parent_concept_id": "fractions.common-denominators",
        "prerequisite_concept_ids": ["fractions.common-denominators", "number.addition"],
    },
    {
        "concept_id": "fractions.subtracting",
        "name": "Subtracting Fractions",
        "description": "Subtracting fractions with like and unlike denominators",
        "subject": "mathematics",
        "grade_level_min": 4,
        "grade_level_max": 6,
        "exam_standard": "NCDPI",
        "parent_concept_id": "fractions.common-denominators",
        "prerequisite_concept_ids": ["fractions.common-denominators", "number.subtraction"],
    },
    {
        "concept_id": "fractions.multiplying",
        "name": "Multiplying Fractions",
        "description": "Multiplying fractions and mixed numbers",
        "subject": "mathematics",
        "grade_level_min": 5,
        "grade_level_max": 7,
        "exam_standard": "NCDPI",
        "parent_concept_id": "fractions.basics",
        "prerequisite_concept_ids": ["fractions.basics", "number.multiplication"],
    },
    {
        "concept_id": "fractions.dividing",
        "name": "Dividing Fractions",
        "description": "Dividing fractions using reciprocals",
        "subject": "mathematics",
        "grade_level_min": 5,
        "grade_level_max": 7,
        "exam_standard": "NCDPI",
        "parent_concept_id": "fractions.multiplying",
        "prerequisite_concept_ids": ["fractions.multiplying", "number.division"],
    },
    
    # Decimals
    {
        "concept_id": "decimals.basics",
        "name": "Decimal Basics",
        "description": "Understanding decimals and place value",
        "subject": "mathematics",
        "grade_level_min": 4,
        "grade_level_max": 6,
        "exam_standard": "NCDPI",
        "parent_concept_id": None,
        "prerequisite_concept_ids": ["number.place-value", "fractions.basics"],
    },
    {
        "concept_id": "decimals.operations",
        "name": "Decimal Operations",
        "description": "Adding, subtracting, multiplying, and dividing decimals",
        "subject": "mathematics",
        "grade_level_min": 5,
        "grade_level_max": 7,
        "exam_standard": "NCDPI",
        "parent_concept_id": "decimals.basics",
        "prerequisite_concept_ids": ["decimals.basics", "number.multiplication"],
    },
    
    # Geometry
    {
        "concept_id": "geometry.shapes",
        "name": "Basic Shapes",
        "description": "Identifying and classifying 2D and 3D shapes",
        "subject": "mathematics",
        "grade_level_min": 3,
        "grade_level_max": 5,
        "exam_standard": "NCDPI",
        "parent_concept_id": None,
        "prerequisite_concept_ids": [],
    },
    {
        "concept_id": "geometry.perimeter",
        "name": "Perimeter",
        "description": "Calculating perimeter of polygons",
        "subject": "mathematics",
        "grade_level_min": 3,
        "grade_level_max": 5,
        "exam_standard": "NCDPI",
        "parent_concept_id": "geometry.shapes",
        "prerequisite_concept_ids": ["geometry.shapes", "number.addition"],
    },
    {
        "concept_id": "geometry.area",
        "name": "Area",
        "description": "Calculating area of rectangles and other shapes",
        "subject": "mathematics",
        "grade_level_min": 4,
        "grade_level_max": 6,
        "exam_standard": "NCDPI",
        "parent_concept_id": "geometry.shapes",
        "prerequisite_concept_ids": ["geometry.shapes", "number.multiplication"],
    },
    
    # Algebra Basics
    {
        "concept_id": "algebra.patterns",
        "name": "Patterns and Sequences",
        "description": "Identifying and extending patterns",
        "subject": "mathematics",
        "grade_level_min": 3,
        "grade_level_max": 5,
        "exam_standard": "NCDPI",
        "parent_concept_id": None,
        "prerequisite_concept_ids": ["number.addition"],
    },
    {
        "concept_id": "algebra.expressions",
        "name": "Algebraic Expressions",
        "description": "Writing and evaluating simple algebraic expressions",
        "subject": "mathematics",
        "grade_level_min": 5,
        "grade_level_max": 7,
        "exam_standard": "NCDPI",
        "parent_concept_id": "algebra.patterns",
        "prerequisite_concept_ids": ["algebra.patterns", "number.multiplication"],
    },
    {
        "concept_id": "algebra.equations",
        "name": "Solving Equations",
        "description": "Solving one-step and two-step equations",
        "subject": "mathematics",
        "grade_level_min": 6,
        "grade_level_max": 8,
        "exam_standard": "NCDPI",
        "parent_concept_id": "algebra.expressions",
        "prerequisite_concept_ids": ["algebra.expressions"],
    },
    
    # Data and Probability
    {
        "concept_id": "data.graphs",
        "name": "Reading Graphs",
        "description": "Interpreting bar graphs, line graphs, and pie charts",
        "subject": "mathematics",
        "grade_level_min": 3,
        "grade_level_max": 5,
        "exam_standard": "NCDPI",
        "parent_concept_id": None,
        "prerequisite_concept_ids": [],
    },
    {
        "concept_id": "data.mean-median-mode",
        "name": "Mean, Median, Mode",
        "description": "Calculating measures of central tendency",
        "subject": "mathematics",
        "grade_level_min": 5,
        "grade_level_max": 7,
        "exam_standard": "NCDPI",
        "parent_concept_id": "data.graphs",
        "prerequisite_concept_ids": ["data.graphs", "number.division"],
    },
]


def get_concept_by_id(concept_id: str):
    """Get a concept by its ID."""
    for concept in NCDPI_MATH_CONCEPTS:
        if concept["concept_id"] == concept_id:
            return concept
    return None


def get_concepts_by_grade(grade_level: int):
    """Get all concepts appropriate for a grade level."""
    return [
        c for c in NCDPI_MATH_CONCEPTS
        if c["grade_level_min"] <= grade_level <= c["grade_level_max"]
    ]


def get_prerequisite_chain(concept_id: str):
    """Get the full chain of prerequisites for a concept."""
    concept = get_concept_by_id(concept_id)
    if not concept:
        return []
    
    chain = []
    for prereq_id in concept.get("prerequisite_concept_ids", []):
        chain.append(prereq_id)
        chain.extend(get_prerequisite_chain(prereq_id))
    
    return list(set(chain))  # Remove duplicates
