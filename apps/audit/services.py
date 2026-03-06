from .models import AuditLog

class AuditLogger:
    @staticmethod
    def log(actor, action_type, entity, metadata=None):
        """
        actor: User object
        action_type: String (e.g., 'STUDENT_GRADUATE')
        entity: The model instance being acted upon
        metadata: Dictionary of extra context
        """
        AuditLog.objects.create(
            actor=actor,
            action_type=action_type,
            entity_type=entity.__class__.__name__,
            entity_id=str(entity.pk),
            metadata=metadata or {}
        )