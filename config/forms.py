from django import forms


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(max_length=128, widget=forms.PasswordInput)
    new_password = forms.CharField(max_length=128, widget=forms.PasswordInput)
    confirm_new_password = forms.CharField(max_length=128, widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_new_password = cleaned_data.get("confirm_new_password")
        if (
            new_password
            and confirm_new_password
            and new_password != confirm_new_password
        ):
            raise forms.ValidationError("새로운 비밀번호와 확인용 비밀번호가 일치하지 않습니다")

        return cleaned_data
