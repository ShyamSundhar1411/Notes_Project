import os
from io import BytesIO
from xhtml2pdf import pisa
from django.conf import settings
from django.views import generic
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.shortcuts import render,redirect,get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http.response import Http404, HttpResponse
from django.template.loader import get_template
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from . models import Note,Profile
from . forms import NoteCreationForm,UserForm,ProfileForm
from . filters import NoteFilter
from . tasks import send_requested_pdf,send_requested_pdf_on_delete
# Create your views here.
#Class Based
class NoteDetailView(LoginRequiredMixin,generic.DetailView):
    model = Note
    slug_field = Note.slug
    template_name = "lazynotes/NoteDetail.html"
    fields = ['title','notes','subject','updated_on']
    def get_object(self):
        note = super(NoteDetailView,self).get_object()
        if not note.user == self.request.user:
            raise Http404
        return note
class NoteUpdateView(LoginRequiredMixin,generic.UpdateView):
    model = Note
    slug_field = Note.slug
    template_name = "lazynotes/NoteUpdate.html"
    fields = ['title','subject','notes']
    def get_object(self):
        note = super(NoteUpdateView,self).get_object()
        if not note.user == self.request.user:
            raise Http404
        return note
    def get_success_url(self):
        pk = self.kwargs["pk"]
        slug = self.kwargs["slug"]
        messages.success(self.request,'Updated Successfully')
        return reverse("note_detail", kwargs={"slug":slug,"pk": pk})
class NoteDeleteView(LoginRequiredMixin,generic.DeleteView):
    model = Note
    slug_field = Note.slug
    template_name = "lazynotes/NoteDelete.html"
    def get_object(self):
        note = super(NoteDeleteView,self).get_object()
        if not note.user == self.request.user:
            raise Http404
        return note
    def get_success_url(self):
        note = super(NoteDeleteView,self).get_object()
        render_pdf_send_mail_on_delete(self.request,note.id)
        return reverse('home')
class ViewAllNotes(LoginRequiredMixin,generic.ListView):
    model = Note
    template_name = 'lazynotes/viewallnotes.html'
    def get_queryset(self):
        return Note.objects.filter(user = self.request.user)
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['filterer'] = NoteFilter(self.request.GET,queryset = self.get_queryset())
        return context
#Function Based
@login_required
def home(request):
    note = Note.objects.filter(user = request.user).order_by('-updated_on')
    page = request.GET.get('page', 1)
    paginator = Paginator(note,3)
    note_count = paginator.count
    try:
        notes = paginator.page(page)
    except PageNotAnInteger :
        notes = paginator.page(1)
    except EmptyPage:
        notes = paginator.page(paginator.num_pages)
    return render(request,'lazynotes/home.html',{"Notes":notes,'note_count':note_count})
@login_required
def viewallnotes(request):
    notes = Note.objects.filter(user = request.user).order_by('-updated_on')
    return render(request,'lazynotes/viewallnotes.html',{"Notes":notes})
@login_required
def create_note(request):
    if request.method=='POST':
        try:
            form = NoteCreationForm(request.POST,request.FILES)
            newform = form.save(commit=False)
            newform.user = request.user
            newform.save()
            return redirect('home')
        except ValueError:
            return render(request, 'lazynotes/add_notes.html', {'form':NoteCreationForm(), 'error': messages.error(request,'Bad data passed in. Try again.')})
    else:
        return render(request,'lazynotes/add_notes.html',{'form':NoteCreationForm()})
@login_required
def profile(request,slug):
    if request.method == 'POST':
        user_form = UserForm(request.POST,instance = request.user)
        profile_form = ProfileForm(request.POST,request.FILES,instance = request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,'Profile Update Successfully')
            return redirect('profile',slug = request.user.profile.slug)
        else:
            return render(request, 'account/profile.html', {'user_form':user_form,'profile_form':profile_form,'user_form_errors':user_form.errors,'profile_form_errors':profile_form.errors})
    else:
        user_form = UserForm(instance = request.user)
        profile_form = ProfileForm(instance = request.user.profile)
    return render(request,'account/profile.html',{'user_form':user_form,'profile_form':profile_form})
#pdf
@login_required
def render_pdf_download(request,pk):
    template_path = "lazynotes/note.html"
    note = get_object_or_404(Note,pk = pk, user = request.user)
    context = {"Note":note}
    links    = lambda uri, rel: os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
    response = HttpResponse(content_type = "application/pdf")
    response['Content-Disposition'] = 'attachment; filename = {}.pdf'.format(note.title)
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(
        html,dest = response,link_callback = links)
    if pisa_status.err:
        return HttpResponse("We had some errors <pre>"+html+"</pre>")
    return response
@login_required
def render_pdf_send_mail(request,pk):
    template_path = "lazynotes/note.html"
    note = get_object_or_404(Note,pk = pk, user = request.user)
    context = {"Note":note}
    template = get_template(template_path)
    html = template.render(context)
    links    = lambda uri, rel: os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")),result,link_callback = links)
    pdf = result.getvalue()
    filename = str(note.title)+'.pdf'
    send_requested_pdf(filename,pdf,request.user.id)
    messages.info(request,"The requested PDF has been sent to the registered email.")
    return redirect('note_detail',note.id,note.slug)
@login_required
def render_pdf_send_mail_on_delete(request,pk):
    template_path = "lazynotes/note.html"
    note = get_object_or_404(Note,pk = pk, user = request.user)
    context = {"Note":note}
    template = get_template(template_path)
    html = template.render(context)
    links    = lambda uri, rel: os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")),result,link_callback = links)
    pdf = result.getvalue()
    filename = str(note.title)+'(BackUp).pdf'
    send_requested_pdf_on_delete(filename,pdf,request.user.id)
    messages.info(request,"Deletion Successful.A backup of this note has been sent to the registered email.")