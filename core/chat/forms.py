from django import forms
from .models import     Profile
from django.contrib.auth import get_user_model

User = get_user_model()

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields  = ['profile']

    def save(self, commit=True):
        """Override save to upload profile image to Cloudinary and store only public_id.

        This prevents storing full Cloudinary URLs in the DB which cause 404s
        when the application later builds the display URL.
        """
        instance = super().save(commit=False)
        uploaded = self.cleaned_data.get('profile')

        if uploaded:
            try:
                from cloudinary import uploader
                from django.conf import settings
                cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', None)

                # Build a predictable public_id in a user_profiles folder
                uid = getattr(instance, 'user', None)
                uid_part = getattr(uid, 'id', None) or getattr(uid, 'pk', None) or 'anon'
                base_name = getattr(uploaded, 'name', 'profile').rsplit('.', 1)[0]
                public_id = f"user_profiles/{uid_part}_{base_name}"

                # Ensure file pointer at start
                if hasattr(uploaded, 'seek'):
                    try:
                        uploaded.seek(0)
                    except Exception:
                        pass

                result = uploader.upload(
                    uploaded,
                    public_id=public_id,
                    resource_type='image',
                    overwrite=True,
                    use_filename=False,
                    unique_filename=False
                )

                # uploader returns public_id like 'user_profiles/123_name'
                returned_public_id = result.get('public_id') if isinstance(result, dict) else None
                if returned_public_id:
                    instance.profile = returned_public_id
            except Exception:
                # On failure, fall back to default behavior (let storage/backend handle it)
                pass

        if commit:
            instance.save()
        return instance

class DeliveryAddressForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['province', 'municipality', 'street', 'postal_code']

class UpdateUser(forms.ModelForm):
    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}),
        }
class VerifyUserForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


# forms.py (add below the previous form)
class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new = cleaned_data.get("new_password")
        confirm = cleaned_data.get("confirm_password")
        if new != confirm:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
