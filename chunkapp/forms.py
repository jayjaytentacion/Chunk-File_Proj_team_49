from dataclasses import fields
from django import forms
#from . utils import validateFile
from . models import ChunkOrder
from django.forms import ModelForm


# this is the form that takes in the required entries to chunk a file
# the file to be chunked is also uploaded within this form along with
# the size of chunks
# class ChunkOrderForm(forms.Form):
#     # the file field is for the file that is to be uploaded
#     # the chunk size is to determine how the file is going to be chunked
#     file = forms.FileField(validators=[validateFile])
#     chunk_size = forms.IntegerField()

class FileUploadForm(ModelForm):
    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs) 
        self.fields['file'].widget.attrs.update({ 
            'id':'file', 
            'type':'file',  
            "onchange":"validateUploadedFile(event)"
            })
    class Meta:
        model=ChunkOrder
        fields=['file']

class ChunkSizeForm(ModelForm):
    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs) 
        self.fields['chunk_size'].widget.attrs.update({ 
            'name':'number', 
            'id':'number', 
            'type':'number',  
            "class":"ps-4 pe-3",
             "placeholder":"01",
             "min":"500" ,
             "max":"500000", 
             "onchange":"validateInputNumber()",
            })
    class Meta:
        model=ChunkOrder
        fields=['chunk_size']


class ContactForm(forms.Form):
    email = forms.EmailField(label='Your email')
    message = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs) 
        self.fields['email'].widget.attrs.update({ 
            'type':'email',  
            "placeholder":"johndoe@gmail.com",
            })
    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs) 
        self.fields['message'].widget.attrs.update({ 
            'type':'email', 
            "rows":"10", 
            "placeholder":"Enter your message",
            })            


# class Upload(ModelForm):
#     def __init__(self, *args, **kwargs): 
#         super().__init__(*args, **kwargs) 
#         #self.fields['chunk_size'].widget.attrs.update
#     class Meta:
#         model=zipModel
#         fields=['object']