from django import forms

from .models import Invitation


class SendInvitationForm(forms.ModelForm):

    class Meta:
        model = Invitation
        fields = ('email', )
