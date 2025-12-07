"""
Resources for import/export functionality in app_config.
"""

from import_export import resources
from .models import Permission


class PermissionResource(resources.ModelResource):
    """
    Resource for importing/exporting Permission model.
    """

    class Meta:
        model = Permission
        fields = ('id', 'name', 'codename', 'resource', 'action', 'description', 'is_active', 'created_at', 'updated_at')
        export_order = ('id', 'name', 'codename', 'resource', 'action', 'description')
        import_id_fields = ['codename']
        skip_unchanged = True
        report_skipped = False

