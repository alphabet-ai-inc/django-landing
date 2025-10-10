from django import forms


class ImportPageForm(forms.Form):
    url = forms.URLField(
        label='Page URL',
        widget=forms.URLInput(attrs={
            'placeholder': 'https://example.com/page',
            'class': 'vTextField',
            'style': 'width: 100%;'
        }),
        help_text='Enter the URL of the page you want to import'
    )