from django import forms


class UploadFileForm(forms.Form):
    video = forms.FileField()


class UploadRubeLinkForm(forms.Form):
    r_tube_link = forms.TextInput



