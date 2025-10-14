from django import forms
from main.models import School
class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ['name', 'address', 'email', 'tel', 'headletter', 'approved']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'tel': forms.TextInput(attrs={'class': 'form-control'}),
            'headletter': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
