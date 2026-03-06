class AppPermissions:
    # Sunday School Module
    SS_VIEW = "sundayschool:view"
    SS_EDIT = "sundayschool:edit"
    SS_APPROVE_ATTENDANCE = "sundayschool:approve_attendance"
    
    # Melody Module
    MELODY_OFFICER = "melody:draft_request"
    MELODY_EXEC = "melody:approve_request"
    
    # System Admin / God Mode
    SYSTEM_MANAGE = "identity:all"

    @classmethod
    def as_choices(cls):
        return [(value, value.replace(':', ' ').title()) 
                for key, value in cls.__dict__.items() if not key.startswith('__') and not callable(value)]