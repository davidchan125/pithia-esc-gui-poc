from django import forms


class SimpleSearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SimpleSearchForm, self).__init__(*args, **kwargs)
        self.fields['query'].strip = False

    query = forms.CharField(
        label='Search',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter a term or phrase...',
        })
    )

    exact = forms.BooleanField(
        label='Exact match',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )