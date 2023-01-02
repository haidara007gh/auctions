from django import forms

class NewListingForm(forms.Form):
    title = forms.CharField()
    description = forms.CharField()
    price = forms.FloatField(label="Starting bid")
    url = forms.ImageField(label="Photo")
    category = forms.CharField()

class NewBiddingForm(forms.Form):
    price = forms.FloatField(label="", widget=forms.NumberInput(attrs={"placeholder":"Bid"}))

class NewCommentForm(forms.Form):
    message = forms.CharField(label="",widget=forms.Textarea(attrs={"placeholder":"Leave a comment here"}))