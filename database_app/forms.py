from crispy_forms.helper import FormHelper
from django import forms
from diagram_chase_database.settings import MAX_TEXT_LENGTH

class FunctorForm(forms.Form):
   notation = forms.CharField(
      label="Notation",
      max_length=MAX_TEXT_LENGTH,
      required=True)
   
   category = forms.CharField(
      label="Into Category",
      max_length=MAX_TEXT_LENGTH,
      required=True)