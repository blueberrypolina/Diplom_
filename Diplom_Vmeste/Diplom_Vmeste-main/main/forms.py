from django import forms
from .models import User

class UserForm(forms.ModelForm):
    cyber_crimes = forms.MultipleChoiceField(
        choices=User.CRIME_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input',
            # при необходимости: 'style': 'margin-right:0.5rem;'
        }),
        required=False,  # если не обязательно
    )

    class Meta:
        model = User
        fields = '__all__'
