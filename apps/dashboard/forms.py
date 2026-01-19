from django import forms

class ImportarExcelForm(forms.Form):
    archivo = forms.FileField(
        label="Archivo Excel",
        help_text="Solo archivos .xlsx"
    )