from django.http.response import Http404
from django.shortcuts import render,redirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Note
from .forms import NoteCreationForm
# Create your views here.
#Class Based
class NoteDetailView(generic.DetailView):
    model = Note
    slug_field = Note.slug
    template_name = "lazynotes/NoteDetail.html"
    fields = ['title','notes','subject','updated_on']
class NoteUpdateView(generic.UpdateView):
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
        return reverse("note_update", kwargs={"slug":slug,"pk": pk})
class NoteDeleteView(generic.DeleteView):
    model = Note
    slug_field = Note.slug
    template_name = "lazynotes/NoteDelete.html"
    success_url = reverse_lazy('home')
    def get_object(self):
        note = super(NoteDeleteView,self).get_object()
        if not note.user == self.request.user:
            raise Http404
        return note
#Function Based
@login_required
def home(request):
    notes = Note.objects.filter(user = request.user).order_by('-updated_on')
    return render(request,'lazynotes/home.html',{"Notes":notes})
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
