# from django import forms
# from .models import Role, Permission, UserAccount

# class RoleForm(forms.ModelForm):
#     permissions = forms.ModelMultipleChoiceField(
#         queryset=Permission.objects.all(),
#         widget=forms.CheckboxSelectMultiple,
#         required=False
#     )

#     class Meta:
#         model = Role
#         fields = ['name', 'description', 'permissions']
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Attendance Officer'}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
#         }

# class OfficerRegistrationForm(forms.Form):
#     # People Fields
#     first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
#     father_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
#     grandfather_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
#     sex = forms.ChoiceField(choices=Christian.SEX_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
#     email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
#     phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}))
#     address = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
#     date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control'}))
#     baptism_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control'}))
#     baptism_place = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    

#     # SS Student Fields
#     grade = forms.ModelChoiceField(queryset=Grade.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
#     section = forms.ModelChoiceField(queryset=Section.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
#     joined_year_eth = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
#     status = forms.ModelChoiceField(queryset=StudentStatus.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    

#     # System Role
#     role = forms.ModelChoiceField(queryset=Role.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
