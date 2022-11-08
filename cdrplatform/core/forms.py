from django import forms


class NewAPIKey(forms.Form):

    name = forms.CharField()
    test_key = forms.BooleanField()
