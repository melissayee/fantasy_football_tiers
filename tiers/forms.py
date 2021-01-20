from django import forms

SCORING_CHOICES = [
    ('standard', 'Standard'),
    ('HALF', 'Half PPR'),
    ('PPR', 'PPR'),
]


class TeamForm(forms.Form):
    url = forms.CharField(label='URL', max_length=200)
    scoring = forms.CharField(label='Scoring', widget=forms.Select(choices=SCORING_CHOICES))
