# Documentation - app_attendance

## Vue d'ensemble

L'application `app_attendance` gère les présences, absences et justificatifs des élèves.

## Modèles

### AttendanceRule
Représente une règle de présence définissant les seuils d'absences.

**Champs principaux :**
- `name` : Nom de la règle
- `max_absences` : Nombre maximum d'absences autorisées
- `alert_threshold` : Seuil déclenchant une alerte
- `period_days` : Période en jours pour le calcul

**Méthodes :**
- `get_rule(id)` : Récupère une règle active par ID

### Attendance
Représente une présence quotidienne d'un élève.

**Champs principaux :**
- `student` : ForeignKey vers app_profile.Student
- `class_section` : ForeignKey vers app_academic.Class
- `date` : Date de la présence
- `status` : Statut (present, absent, late, excused)
- `time_in` : Heure d'arrivée
- `time_out` : Heure de départ
- `notes` : Notes supplémentaires

**Méthodes :**
- `get_attendance(id)` : Récupère une présence active par ID
- `get_attendance_by_student(student_id, start_date, end_date)` : Récupère les présences d'un élève sur une période
- `get_attendance_by_class(class_id, date)` : Récupère les présences d'une classe pour une date

### Absence
Représente une absence d'un élève.

**Champs principaux :**
- `student` : ForeignKey vers app_profile.Student
- `start_date` : Date de début
- `end_date` : Date de fin (si absence sur plusieurs jours)
- `reason` : Motif de l'absence
- `is_justified` : Indique si l'absence est justifiée
- `justified_by` : ForeignKey vers app_profile.Teacher

**Méthodes :**
- `get_absence(id)` : Récupère une absence active par ID
- `get_absences_by_student(student_id)` : Récupère toutes les absences d'un élève

### Excuse
Représente un justificatif d'absence.

**Champs principaux :**
- `absence` : OneToOneField vers Absence
- `document` : FileField (PDF, image)
- `status` : Statut (pending, approved, rejected)
- `reviewed_by` : ForeignKey vers app_profile.Teacher
- `reviewed_at` : Date d'examen
- `notes` : Notes sur le justificatif

**Méthodes :**
- `get_excuse(id)` : Récupère un justificatif actif par ID
- `approve_excuse(teacher_id)` : Approuve le justificatif
- `reject_excuse(teacher_id, reason)` : Rejette le justificatif

## Services

### app_attendance/services/utils.py

**Fonctions :**
- `calculate_attendance_rate(student_id, start_date, end_date)` : Calcule le taux de présence d'un élève
- `check_absence_threshold(student_id, rule_id)` : Vérifie si un élève a dépassé le seuil d'absences
- `send_absence_alert(student_id)` : Envoie une alerte pour absences répétées (TODO)

## Relations

- `Attendance.student` → ForeignKey vers `app_profile.Student`
- `Attendance.class_section` → ForeignKey vers `app_academic.Class`
- `Absence.student` → ForeignKey vers `app_profile.Student`
- `Absence.justified_by` → ForeignKey vers `app_profile.Teacher`
- `Excuse.absence` → OneToOneField vers `Absence`
- `Excuse.reviewed_by` → ForeignKey vers `app_profile.Teacher`

