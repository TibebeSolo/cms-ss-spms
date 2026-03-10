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
        choices = []
        for key, value in cls.__dict__.items():
            # Only pick up upper-case constants that are strings
            if key.isupper() and isinstance(value, str):
                choices.append((value, value.replace(':',' ').title()))
        return choices