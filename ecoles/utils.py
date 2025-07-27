import os, uuid, datetime
from django.utils.text import slugify

def generic_upload_to(instance, filename):
    """
    Chemin de stockage réutilisable pour tout ImageField/FileField.

    • Classe ➜ <app>/<model>/
    • Nom de fichier lisible ➜ <slug|pk|uuid>.<ext>
    • Aucun conflit : UUID ajouté
    • Django crée les dossiers manquants.
    """
    # dossier = nom_app / nom_model (minuscule)
    app_label  = instance._meta.app_label
    model_name = instance._meta.model_name           # déjà lower-case
    folder = f"{app_label}/{model_name}"

    # base lisible : slug si présent, sinon pk (si déjà sauvé), sinon horodatage
    base, ext = os.path.splitext(filename)
    if getattr(instance, "slug", None):
        base = slugify(instance.slug or base)
    elif getattr(instance, "pk", None):
        base = str(instance.pk)
    else:
        base = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    # uuid pour éviter toute collision
    unique_id = uuid.uuid4().hex[:8]
    new_name  = f"{base}_{unique_id}{ext.lower()}"

    return os.path.join(folder, new_name)
