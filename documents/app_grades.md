# Documentation - app_grades

## Vue d'ensemble

L'application `app_grades` gère les notes, évaluations et bulletins scolaires.

## Modèles

### GradeScale
Représente un barème de notation (ex: 0-20, A-F).

**Champs principaux :**
- `name` : Nom du barème
- `min_score` : Note minimale
- `max_score` : Note maximale
- `passing_score` : Note de passage

**Méthodes :**
- `get_grade_scale(id)` : Récupère un barème actif par ID

### GradeCategory
Représente une catégorie d'évaluation (Contrôle continu, Examen, etc.).

**Champs principaux :**
- `name` : Nom de la catégorie
- `code` : Code unique
- `weight` : Poids pour le calcul de moyenne

**Méthodes :**
- `get_category(id)` : Récupère une catégorie active par ID

### Assessment
Représente une évaluation (devoir, contrôle, examen).

**Champs principaux :**
- `name` : Nom de l'évaluation
- `subject` : ForeignKey vers app_academic.Subject
- `class_section` : ForeignKey vers app_academic.Class
- `category` : ForeignKey vers GradeCategory
- `date` : Date de l'évaluation
- `coefficient` : Coefficient de l'évaluation
- `max_score` : Note maximale possible
- `academic_year` : ForeignKey vers app_academic.AcademicYear

**Méthodes :**
- `get_assessment(id)` : Récupère une évaluation active par ID
- `get_assessments_by_class(class_id)` : Récupère les évaluations d'une classe

### StudentGrade
Représente une note d'un élève pour une évaluation.

**Champs principaux :**
- `student` : ForeignKey vers app_profile.Student
- `assessment` : ForeignKey vers Assessment
- `score` : Note obtenue
- `comment` : Commentaire
- `is_absent` : Indique si l'élève était absent

**Méthodes :**
- `get_student_grade(id)` : Récupère une note active par ID
- `get_grades_by_student(student_id)` : Récupère toutes les notes d'un élève
- `calculate_average(student_id, subject_id, year_id)` : Calcule la moyenne d'un élève pour une matière

### ReportCard
Représente un bulletin de notes.

**Champs principaux :**
- `student` : ForeignKey vers app_profile.Student
- `academic_year` : ForeignKey vers app_academic.AcademicYear
- `term` : Trimestre/Semestre
- `overall_average` : Moyenne générale
- `rank` : Classement
- `total_students` : Nombre total d'élèves

**Méthodes :**
- `get_report_card(id)` : Récupère un bulletin actif par ID
- `generate_report_card(student_id, year_id, term)` : Génère ou récupère un bulletin

## Services

### app_grades/services/utils.py

**Fonctions :**
- `calculate_student_average(student_id, subject_id, year_id)` : Calcule la moyenne d'un élève pour une matière
- `calculate_class_average(class_id, assessment_id)` : Calcule la moyenne de classe pour une évaluation
- `calculate_overall_average(student_id, year_id)` : Calcule la moyenne générale d'un élève
- `generate_report_card_pdf(report_card_id)` : Génère un PDF pour un bulletin (TODO)

## Relations

- `Assessment.subject` → ForeignKey vers `app_academic.Subject`
- `Assessment.class_section` → ForeignKey vers `app_academic.Class`
- `StudentGrade.student` → ForeignKey vers `app_profile.Student`
- `ReportCard.student` → ForeignKey vers `app_profile.Student`

