from django import forms
from people.models import Christian
from identity.models import Role
from .models import Grade, Section

class StudentOfficerRegistrationForm(forms.Form):
    # Personal info
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    father_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    grandfather_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    baptismal_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    sex = forms.ChoiceField(choices=Christian.SEX_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    photo = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}))

    # Address
    region = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    town_city = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    kebele = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    home_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    # Contact Person
    contact_full_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}))
    contact_relationship = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Father, Mother'}))
    contact_phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}))
    contact_address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Address'}))

    # Sunday school info
    grade = forms.ModelChoiceField(queryset=Grade.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    section = forms.ModelChoiceField(queryset=Section.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    confession_father_name = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Full Name of Confession Father'})
    )
    joined_year_eth = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))

    # Hidden or visible Role field
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(), 
        required=False, 
        empty_label="No Admin Role (Regular Student)",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Only show the Role field to System Admins
        if user and not user.is_superuser and not user.groups.filter(name='System Admin').exists():
            self.fields['role'].widget = forms.HiddenInput()