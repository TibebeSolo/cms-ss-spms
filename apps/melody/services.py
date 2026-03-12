from django.db import transaction
from django.conf import settings
from .models import MezemranMembership, MezemranChangeRequest
from django.utils import timezone

class MelodyIDService:
    @staticmethod
    @transaction.atomic
    def generate_mez_id(entry_year_eth):
        """
        Generates ID: {SSAbbrev}MZ{YY}{RRR}
        Example: ABSSMZ16001
        """
        from org.models import SundaySchool
        ss = SundaySchool.objects.filter(is_active=True).first()
        ss_prefix = ss.abbreviation if ss else "SS"

        year_yy = str(entry_year_eth)[-2:]
        
        # Scope roll number to the entry year
        last_mez = MezemranMembership.objects.filter(
            mezmur_entry_year_eth=entry_year_eth
        ).select_for_update().order_by('-mezemran_roll_number').first()
        
        roll = (last_mez.mezemran_roll_number + 1) if last_mez else 1
        
        # Note the "MZ" constant in the middle
        generated_id = f"{ss_prefix}MZ{year_yy}{roll:03d}"
        return generated_id, roll

class MezemranWorkflowService:
    
    @staticmethod
    @transaction.atomic
    def submit_to_exec(request_id):
        """Moves a DRAFT request to PENDING_MELODY_EXEC."""
        request = MezemranChangeRequest.objects.select_for_update().get(id=request_id)
        if request.state == 'DRAFT':
            request.state = 'PENDING_MELODY_EXEC'
            request.save()
        return request

    @staticmethod
    @transaction.atomic
    def exec_approve(request_id, user, comment):
        """Melody Exec approves; moves to PENDING_LEADER."""
        request = MezemranChangeRequest.objects.select_for_update().get(id=request_id)
        if request.state == 'PENDING_MELODY_EXEC':
            request.state = 'PENDING_LEADER'
            request.melody_exec_approved_by = user
            request.melody_exec_approved_at = timezone.now()
            request.melody_exec_comment = comment
            request.save()
        return request

    @staticmethod
    @transaction.atomic
    def final_leader_approve(request_id, user, comment):
        """SS Leader approves; Triggers the actual Membership change."""
        request = MezemranChangeRequest.objects.select_for_update().get(id=request_id)
        if request.state != 'PENDING_LEADER':
            raise ValueError("Request is not in the correct state for Leader approval.")

        # 1. Finalize Request state
        request.state = 'APPROVED'
        request.leader_approved_by = user
        request.leader_approved_at = timezone.now()
        request.leader_comment = comment
        request.save()

        # 2. Execute the Business Logic based on action_type
        if request.action_type == 'SELECT':
            MezemranWorkflowService._execute_selection(request)
        elif request.action_type == 'TERMINATE':
            MezemranWorkflowService._execute_termination(request)
            
        
        AuditLogger.log(
            actor=user,
            action_type=f"MEZEMRAN_{request.action_type}_APPROVED",
            entity=request,
            metadata={
                "request_id": request.id,
                "student_id": request.ss_student_profile.id,
                "comment": comment
            }
        )
        return request

    @staticmethod
    def _execute_selection(request):
        """Internal helper to create membership after final approval."""
        from .services import MelodyIDService # Your ID Generator from Step 4
        
        # Payload contains: selection_reason, criteria_used, entry_year
        payload = request.payload 
        
        mez_id, roll = MelodyIDService.generate_mez_id(payload['entry_year'])
        
        MezemranMembership.objects.create(
            ss_student_profile=request.ss_student_profile,
            mezmur_entry_year_eth=payload['entry_year'],
            mezemran_roll_number=roll,
            mezemran_id=mez_id,
            selected_at=timezone.now(),
            selected_by=request.drafted_by,
            selection_reason=payload.get('reason', ''),
            criteria_used=payload.get('criteria', ''),
            is_active=True
        )

    @staticmethod
    def _execute_termination(request):
        """Internal helper to deactivate membership."""
        membership = request.target_membership
        membership.status = 'TERMINATED'
        membership.is_active = False
        membership.terminated_at = timezone.now()
        membership.terminated_by = request.leader_approved_by
        membership.termination_reason = request.payload.get('reason', 'Official termination')
        membership.save()