# Documentation - app_academic

## Vue d'ensemble

L'application `app_academic` gère toute la structure académique de l'établissement scolaire :
- Années scolaires
- Niveaux (CP, CE1, 6ème, etc.)
- Salles de classe
- Classes/Sections
- Matières
- Cours
- Emploi du temps

## Modèles

### AcademicYear
Représente une année scolaire (ex: 2024-2025).

**Champs principaux :**
- `name` : Nom de l'année (ex: "2024-2025")
- `start_date` : Date de début
- `end_date` : Date de fin
- `is_current` : Indique si c'est l'année courante

**Méthodes :**
- `get_academic_year(id)` : Récupère une année active par ID
- `get_current_year()` : Récupère l'année scolaire courante

### Grade
Représente un niveau scolaire (CP, CE1, 6ème, etc.).

**Champs principaux :**
- `name` : Nom du niveau
- `code` : Code unique
- `order` : Ordre d'affichage

**Méthodes :**
- `get_grade(id)` : Récupère un niveau actif par ID
- `get_all_grades()` : Récupère tous les niveaux actifs

### ClassRoom
Représente une salle de classe.

**Champs principaux :**
- `name` : Nom de la salle
- `capacity` : Capacité maximale
- `floor` : Étage
- `equipment` : Équipements disponibles

**Méthodes :**
- `get_classroom(id)` : Récupère une salle active par ID
- `get_available_classrooms()` : Récupère toutes les salles disponibles

### Class
Représente une classe/section (ex: "6ème A").

**Champs principaux :**
- `name` : Nom de la classe
- `code` : Code unique
- `grade` : ForeignKey vers Grade
- `academic_year` : ForeignKey vers AcademicYear
- `classroom` : ForeignKey vers ClassRoom (optionnel)
- `capacity` : Capacité maximale
- `teacher` : ForeignKey vers app_profile.Teacher (professeur principal)

**Méthodes :**
- `get_class(id)` : Récupère une classe active par ID
- `get_classes_by_year(year_id)` : Récupère toutes les classes d'une année
- `get_students_count()` : Retourne le nombre d'élèves dans la classe

### Subject
Représente une matière (Mathématiques, Français, etc.).

**Champs principaux :**
- `name` : Nom de la matière
- `code` : Code unique
- `coefficient` : Coefficient pour le calcul de moyenne

**Méthodes :**
- `get_subject(id)` : Récupère une matière active par ID
- `get_all_subjects()` : Récupère toutes les matières actives

### Course
Représente un cours (lien entre matière, classe, enseignant et année).

**Champs principaux :**
- `subject` : ForeignKey vers Subject
- `class_section` : ForeignKey vers Class
- `teacher` : ForeignKey vers app_profile.Teacher
- `academic_year` : ForeignKey vers AcademicYear

**Méthodes :**
- `get_course(id)` : Récupère un cours actif par ID
- `get_courses_by_teacher(teacher_id)` : Récupère les cours d'un enseignant
- `get_courses_by_class(class_id)` : Récupère les cours d'une classe

### Schedule
Représente un créneau d'emploi du temps.

**Champs principaux :**
- `course` : ForeignKey vers Course
- `day_of_week` : Jour de la semaine (0=Lundi, 6=Dimanche)
- `start_time` : Heure de début
- `end_time` : Heure de fin
- `classroom` : ForeignKey vers ClassRoom (optionnel)

**Méthodes :**
- `get_schedule(id)` : Récupère un créneau actif par ID
- `get_schedule_by_class(class_id)` : Récupère l'emploi du temps d'une classe
- `get_schedule_by_teacher(teacher_id)` : Récupère l'emploi du temps d'un enseignant

## Relations avec app_profile

- `Student.class_section` → ForeignKey vers `Class`
- `Student.academic_year` → ForeignKey vers `AcademicYear`
- `Teacher.subjects` → ManyToMany vers `Subject`
- `Teacher.classes` → ManyToMany vers `Class`

## Champs obligatoires

Tous les modèles incluent :
- `is_active` : BooleanField (default=True)
- `created_at` : DateTimeField (auto_now_add=True)
- `updated_at` : DateTimeField (auto_now=True)
- `created_by` : ForeignKey vers User (nullable)
- `updated_by` : ForeignKey vers User (nullable)

