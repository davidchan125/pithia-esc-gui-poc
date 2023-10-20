from django import forms


class UploadFileForm(forms.Form):
    files = forms.FileField(
        label='Upload File(s)',
        widget=forms.ClearableFileInput(attrs={
            'accept': 'application/xml',
            'class': 'form-control',
            'allow_multiple_selected': True,
        })
    )


class UploadDataCollectionFileForm(forms.Form):
    files = forms.FileField(
        label='Upload File',
        widget=forms.ClearableFileInput(attrs={
            'accept': 'application/xml',
            'class': 'form-control',
        }))
    api_selected = forms.BooleanField(
        label='API',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    api_specification_url = forms.CharField(
        label='Link to API Specification',
        required=False,
        disabled=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    api_description = forms.CharField(
        label='Description',
        required=False,
        disabled=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'style': 'resize: none;'
        })
    )


class UploadCatalogueDataSubsetFileForm(forms.Form):
    files = forms.FileField(
        label='Upload File',
        widget=forms.ClearableFileInput(attrs={
            'accept': 'application/xml',
            'class': 'form-control',
        })
    )

    register_doi = forms.BooleanField(
        label='Generate DOI for this Data Subset',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
