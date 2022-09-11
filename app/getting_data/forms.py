from django import forms


class DateForm(forms.Form):
    date_from_user = forms.DateTimeField(label='Дата')
