from django import newforms as forms
from models import Position

class PositionForm(forms.ModelForm):
    politician = forms.IntegerField(widget=forms.HiddenInput)
    class Meta:
        model = Position
        exclude = ('creator', 'verified', 'verifier')
