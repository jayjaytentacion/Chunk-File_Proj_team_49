from django.shortcuts import render, redirect,get_object_or_404,HttpResponseRedirect
from . utils import zipFunction,chunkCsv,TEMPLATES,FORMS, chunkJson
from . models import ChunkOrder
from formtools.wizard.views import SessionWizardView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
import pathlib
import threading
from django.contrib.auth.decorators import login_required
import json
from django.http import HttpResponse
from django.contrib import messages
from . forms import ContactForm
from django.core.mail import send_mail,BadHeaderError


MEDIA_DIR = settings.MEDIA_ROOT
# the convention for creating a view is the view function 
# and view appended to the name, this is for simplicity and easy
# understanding of code 
# the view functions use a camelCase convention

#landing page view
def index(request):
    return render(request,'chunkapp/index.html')

#about us view
def about_us(request):
    return render(request,'chunkapp/abt.html')


#frequently asked questions view
def faq(request):
    return render(request,'chunkapp/faq.html')

#terms an conditions view
def termsAndConditions(request):
    return render(request ,'chunkapp/toc.html')    

#how to use view
def howTouse(request):
    return render (request,'chunkapp/howtouse.html')

#account settings view   
@login_required(login_url='accounts:login')
def accountSettings(request):
    return render(request,'chunkapp/accsettings.html')
#contact us view    
# def contactUs(request):
#     return render(request,'chunkapp/contact.html')    

#list recent chunks view
@login_required(login_url='accounts:login')
def listRecentChunks(request):
    recent_chunks=ChunkOrder.objects.filter(custom_user = request.user)
    context={
        'recent_chunks':recent_chunks
    }          
    return render(request,'chunkapp/recent.html',context)

#dashboard upload wizard view
class UploadWizard(LoginRequiredMixin,SessionWizardView):
    login_url = "accounts:login"
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]
    # template_name='chunkapp/dashboard.html'
    form_list = FORMS
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'largefile'))
    #file_storage = FileSystemStorage()
    def done(self,form_list,form_dict, **kwargs):
         try:
             form_data, file, chunk_size =process_form(form_list)
         except:
            messages.error(self.request, 'Error:something unexpected occured.') 
            return redirect('chunkapp:dashboard')   
         else:   
            chunkOrder = ChunkOrder.objects.create(custom_user = self.request.user, zip_link = form_data, file_name = file, chunk_size = chunk_size)
            chunkOrder.save()
            identifier = str(chunkOrder.zip_link).split("/")[2]
            print(identifier)
            return render(self.request, 'chunkapp/dashboard5.html', {'form_data':form_data, 'download': chunkOrder.zip_link, "id": identifier})

def process_form(form_list):
    """
    this function takes the files and the parameter for splitting and calls the respective 
    splitting function depending on the file extension
    """
    form_data =[form.cleaned_data for form in form_list]
    file=form_data[0]['file'].name
    chunk_size=form_data[1]['chunk_size']
    path =pathlib.Path(MEDIA_DIR + "/largefile/" + file)
    if file.endswith('.json'):
        dir=chunkJson(path, chunk_size)  
    elif file.endswith('.csv'):
        dir= chunkCsv(path,chunk_size)    
    return zipFunction(dir), file, chunk_size



def download_zip(request, link):
    """
    this function would delete the automatically saved files ,if the
    user chooses to only download the file
    """
    download = '/media/' +link
    file = open(download, "rb")
    print(file.name)
    chunk_order = ChunkOrder.objects.filter(custom_user = request.user).get(zip_link = download)
    def delete():
        chunk_order.delete()
    if chunk_order != None:
        delay = 86400
        delete_thread = threading.Timer(delay, delete)
        delete_thread.start()
    return redirect("chunkapp:recent")


def contactUs(request):
        if request.method == 'POST':
            form = ContactForm(request.POST)
            if form.is_valid():
                subject = "Website Inquiry" 
                from_email = form.cleaned_data['email']
                message = form.cleaned_data['message'] 
                try:
                   send_mail(subject, message, from_email, ['juliusstan10@gmail.com'])
                   print('works') 
                except BadHeaderError: #add this
                    return HttpResponse('Invalid header found.') #add this
                else :
                    messages.error(request, 'your mail has been sent succesfully.')
                    return render(request, "chunkapp/contact.html", {'form': form})    
        form = ContactForm()
        return render(request, "chunkapp/contact.html", {'form':form})

def delete_view(request,id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    obj = get_object_or_404(ChunkOrder, pk = id)
    if request.method =="POST":
        # delete object
        obj.delete()
        # after deleting redirect to
        # home page
        return redirect("chunkapp:recent")
 
    return render(request, "chunkapp/delete_view.html", context)



# def uploadFile(request):
#     if request.method == 'POST':
#         form = FileUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             # file is saved
#             file=form.save()
#             return render(request, 'chunkapp/new.html', {'form': ChunkSizeForm}) 
#     else:
#         form = FileUploadForm()
#     return render(request, 'chunkapp/dashboard.html', {'form': form,'file':file})

# def setChunkSize(request):
#         form = ChunkSizeForm(request.POST)
#         if form.is_valid():
#             # file is saved
#             file= form.save()
#             return HttpResponse('saved')
#         return render(request, 'chunkapp/new.html', {'form': form})   

#chunk file view
# def chunkFileView(request):
#     # this views primary function is to chunk the uploaded files
#     # it is also responsible for validating the chunk_order_form
#     if request.method == "POST":
#         chunk_order_form = ChunkOrderForm(request.POST, request.FILES)
#         if chunk_order_form.is_valid():
#             # if the form that takes in the chunk order request is valid 
#             # now we can start the chunking process

#             # first we get the type of file that was uploaded
#             # and then download it unto the server
#             file = handleUploadedFile(request.FILES['file'])
#             file_name = file.name
#             file_type = file_name.split(".")[1]
#             chunk_size = chunk_order_form.cleaned_data['chunk_size']
#             file_location = BASE_DIR / file_name
#             chunk_location, file = chunkJson(file_location, chunk_size)
#             zip_link = zipFunction(chunk_location, file)
#             # after the file type is gotten we pass to a function that chunks the file
#             order = ChunkOrder.objects.create(file_name = file_name, chunk_size = chunk_size, zip_link = zip_link)
#             return HttpResponse(file_type)
#         else:
#             # this else case shows that chunk order request was invalid
#             # it then redirects the user back to the dashboard
#             redirect("dashboard")

#dashboard view
# def dashBoard(request):
#     # this views primary function is too render a template
#     # and then pass a form as the context
#     # form= FileUploadForm()
#     # context = {"form": form}
#     return render(request,'chunkapp/dashboard.html')

#dashboard upload wizard

