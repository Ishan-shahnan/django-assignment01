from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.db.models import Q, Count, Sum
from django.contrib import messages
from datetime import date, datetime
from .models import Event, Participant, Category
from .forms import EventForm, ParticipantForm, CategoryForm

# Home page
class HomeView(TemplateView):
    template_name = 'events/event_list.html'  
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        
        #Upcoming Events
        context['upcoming_events'] = Event.objects.select_related('category').prefetch_related('participants').filter(date__gte=today).order_by('date', 'time')[:6]
        
        #Previous Events
        context['previous_events'] = Event.objects.select_related('category').prefetch_related('participants').filter(date__lt=today).order_by('-date', 'time')[:6]
        
        #Cat Search
        context['categories'] = Category.objects.all()
        
        #Aggregate Queery
        context['total_participants'] = Participant.objects.aggregate(total=Count('id'))['total']
        
        return context

#Event Page
class EventsView(ListView):
    model = Event
    template_name = 'events/events.html'
    context_object_name = 'events'

    def get_queryset(self):
        
        queryset = Event.objects.select_related('category').prefetch_related('participants')
        
        #Search
        search = self.request.GET.get('search')
        category = self.request.GET.get('category')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        # Debug: Print search parameters
        if any([search, category, start_date, end_date]):
            print(f"Search params - search: '{search}', category: '{category}', start: '{start_date}', end: '{end_date}'")
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) | 
                Q(location__icontains=search)
            )
            print(f"After search filter: {queryset.count()} events")
        
        if category:
            queryset = queryset.filter(category_id=category)
            print(f"After category filter: {queryset.count()} events")
        
        #Date range filters
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
            print(f"After start_date filter: {queryset.count()} events")
            
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            print(f"After end_date filter: {queryset.count()} events")
            
        return queryset.order_by('-date', '-time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        
        #Total Participant
        context['total_participants'] = Participant.objects.aggregate(total=Count('id'))['total']
        
        return context

#Contact Page
class ContactView(TemplateView):
    template_name = 'events/contact.html'

#Dashboard page
class DashboardView(TemplateView):
    template_name = 'events/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        
        #select_related prefetch_related
        context['events'] = Event.objects.select_related('category').prefetch_related('participants').all().order_by('-date', '-time')
        context['participants'] = Participant.objects.prefetch_related('events').all()
        context['categories'] = Category.objects.all()
        
        #aggregate
        context['total_participants'] = Participant.objects.aggregate(total=Count('id'))['total']
        context['total_events'] = Event.objects.aggregate(total=Count('id'))['total']
        context['total_categories'] = Category.objects.aggregate(total=Count('id'))['total']
        
        
        context['upcoming_events_count'] = Event.objects.filter(date__gte=today).count()
        context['past_events_count'] = Event.objects.filter(date__lt=today).count()
        
        
        context['todays_events'] = Event.objects.select_related('category').prefetch_related('participants').filter(date=today).order_by('time')
        
        
        context['event_form'] = EventForm()
        context['participant_form'] = ParticipantForm()
        context['category_form'] = CategoryForm()
        
        return context
    
    def post(self, request, *args, **kwargs):
        form_type = request.POST.get('form_type')
        
        if form_type == 'event':
            form = EventForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Event created successfully!')
            else:
                #ERROR LOG EVENT
                print("Event form errors:", form.errors)
                error_message = "Error creating event. Please check the form."
                if form.errors:
                    error_details = []
                    for field, errors in form.errors.items():
                        field_name = field.replace('_', ' ').title()
                        error_details.append(f"{field_name}: {', '.join(errors)}")
                    error_message += f" Errors: {', '.join(error_details)}"
                messages.error(request, error_message)
                
        elif form_type == 'participant':
            form = ParticipantForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Participant created successfully!')
            else:
                #ERROR LOG PARTICIPANT
                print("Participant form errors:", form.errors)
                error_message = "Error creating participant. Please check the form."
                if form.errors:
                    error_details = []
                    for field, errors in form.errors.items():
                        field_name = field.replace('_', ' ').title()
                        error_details.append(f"{field_name}: {', '.join(errors)}")
                    error_message += f" Errors: {', '.join(error_details)}"
                messages.error(request, error_message)
                
        elif form_type == 'category':
            form = CategoryForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Category created successfully!')
            else:
                #ERROR LOG CATEGORY
                print("Category form errors:", form.errors)
                error_message = "Error creating category. Please check the form."
                if form.errors:
                    error_details = []
                    for field, errors in form.errors.items():
                        field_name = field.replace('_', ' ').title()
                        error_details.append(f"{field_name}: {', '.join(errors)}")
                    error_message += f" Errors: {', '.join(error_details)}"
                messages.error(request, error_message)
        
        return redirect('events:dashboard')

#Event detailed
class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'
    
    def get_queryset(self):
        return Event.objects.select_related('category').prefetch_related('participants')

#Event CRUD
class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/dashboard.html'
    success_url = reverse_lazy('events:dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today() #Dashboard Context
        context['events'] = Event.objects.select_related('category').prefetch_related('participants').all().order_by('-date', '-time')
        context['participants'] = Participant.objects.prefetch_related('events').all()
        context['categories'] = Category.objects.all()
        context['total_participants'] = Participant.objects.aggregate(total=Count('id'))['total']
        context['total_events'] = Event.objects.aggregate(total=Count('id'))['total']
        context['total_categories'] = Category.objects.aggregate(total=Count('id'))['total']
        context['upcoming_events_count'] = Event.objects.filter(date__gte=today).count()
        context['past_events_count'] = Event.objects.filter(date__lt=today).count()
        context['todays_events'] = Event.objects.filter(date=today).select_related('category').prefetch_related('participants')
        context['event_form'] = EventForm()
        context['participant_form'] = ParticipantForm()
        context['category_form'] = CategoryForm()
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Event created successfully!')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error creating event. Please check the form.')
        return super().form_invalid(form)

class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/dashboard.html'
    success_url = reverse_lazy('events:dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today() #Dashboard context
        context['events'] = Event.objects.select_related('category').prefetch_related('participants').all().order_by('-date', '-time')
        context['participants'] = Participant.objects.prefetch_related('events').all()
        context['categories'] = Category.objects.all()
        context['total_participants'] = Participant.objects.aggregate(total=Count('id'))['total']
        context['total_events'] = Event.objects.aggregate(total=Count('id'))['total']
        context['total_categories'] = Category.objects.aggregate(total=Count('id'))['total']
        context['upcoming_events_count'] = Event.objects.filter(date__gte=today).count()
        context['past_events_count'] = Event.objects.filter(date__lt=today).count()
        context['todays_events'] = Event.objects.filter(date=today).select_related('category').prefetch_related('participants')
        context['event_form'] = self.get_form()  # Use the form instance being edited
        context['participant_form'] = ParticipantForm()
        context['category_form'] = CategoryForm()
        context['editing_event'] = True  # Flag to show we're editing
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Event updated successfully!')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error updating event. Please check the form.')
        return super().form_invalid(form)

class EventDeleteView(DeleteView):
    model = Event
    success_url = reverse_lazy('events:dashboard')
    
    def get(self, request, *args, **kwargs): #delete event
        self.object = self.get_object()
        self.object.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect(self.success_url)

#Participant CRUD
class ParticipantCreateView(CreateView):
    model = Participant
    form_class = ParticipantForm
    template_name = 'events/dashboard.html'
    success_url = reverse_lazy('events:dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today() #Participant Dashboard Context
        context['events'] = Event.objects.select_related('category').prefetch_related('participants').all().order_by('-date', '-time')
        context['participants'] = Participant.objects.prefetch_related('events').all()
        context['categories'] = Category.objects.all()
        context['total_participants'] = Participant.objects.aggregate(total=Count('id'))['total']
        context['total_events'] = Event.objects.aggregate(total=Count('id'))['total']
        context['total_categories'] = Category.objects.aggregate(total=Count('id'))['total']
        context['upcoming_events_count'] = Event.objects.filter(date__gte=today).count()
        context['past_events_count'] = Event.objects.filter(date__lt=today).count()
        context['todays_events'] = Event.objects.filter(date=today).select_related('category').prefetch_related('participants')
        context['event_form'] = EventForm()
        context['participant_form'] = ParticipantForm()
        context['category_form'] = CategoryForm()
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Participant created successfully!')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error creating participant. Please check the form.')
        return super().form_invalid(form)

class ParticipantUpdateView(UpdateView):
    model = Participant
    form_class = ParticipantForm
    template_name = 'events/dashboard.html'
    success_url = reverse_lazy('events:dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        context['events'] = Event.objects.select_related('category').prefetch_related('participants').all().order_by('-date', '-time')
        context['participants'] = Participant.objects.prefetch_related('events').all()
        context['categories'] = Category.objects.all()
        context['total_participants'] = Participant.objects.aggregate(total=Count('id'))['total']
        context['total_events'] = Event.objects.aggregate(total=Count('id'))['total']
        context['total_categories'] = Category.objects.aggregate(total=Count('id'))['total']
        context['upcoming_events_count'] = Event.objects.filter(date__gte=today).count()
        context['past_events_count'] = Event.objects.filter(date__lt=today).count()
        context['todays_events'] = Event.objects.filter(date=today).select_related('category').prefetch_related('participants')
        context['event_form'] = EventForm()
        context['participant_form'] = self.get_form()  # Use the form instance being edited
        context['category_form'] = CategoryForm()
        context['editing_participant'] = True  # Flag to show we're editing
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Participant updated successfully!')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error updating participant. Please check the form.')
        return super().form_invalid(form)

class ParticipantDeleteView(DeleteView):
    model = Participant
    success_url = reverse_lazy('events:dashboard')
    
    def get(self, request, *args, **kwargs): #Delete Participant
        self.object = self.get_object()
        self.object.delete()
        messages.success(request, 'Participant deleted successfully!')
        return redirect(self.success_url)

#Category CRUD
class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'events/dashboard.html'
    success_url = reverse_lazy('events:dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today() #Category Dashboard Context
        context['events'] = Event.objects.select_related('category').prefetch_related('participants').all().order_by('-date', '-time')
        context['participants'] = Participant.objects.prefetch_related('events').all()
        context['categories'] = Category.objects.all()
        context['total_participants'] = Participant.objects.aggregate(total=Count('id'))['total']
        context['total_events'] = Event.objects.aggregate(total=Count('id'))['total']
        context['total_categories'] = Category.objects.aggregate(total=Count('id'))['total']
        context['upcoming_events_count'] = Event.objects.filter(date__gte=today).count()
        context['past_events_count'] = Event.objects.filter(date__lt=today).count()
        context['todays_events'] = Event.objects.filter(date=today).select_related('category').prefetch_related('participants')
        context['event_form'] = EventForm()
        context['participant_form'] = ParticipantForm()
        context['category_form'] = CategoryForm()
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Category created successfully!')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error creating category. Please check the form.')
        return super().form_invalid(form)

class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'events/dashboard.html'
    success_url = reverse_lazy('events:dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        context['events'] = Event.objects.select_related('category').prefetch_related('participants').all().order_by('-date', '-time')
        context['participants'] = Participant.objects.prefetch_related('events').all()
        context['categories'] = Category.objects.all()
        context['total_participants'] = Participant.objects.aggregate(total=Count('id'))['total']
        context['total_events'] = Event.objects.aggregate(total=Count('id'))['total']
        context['total_categories'] = Category.objects.aggregate(total=Count('id'))['total']
        context['upcoming_events_count'] = Event.objects.filter(date__gte=today).count()
        context['past_events_count'] = Event.objects.filter(date__lt=today).count()
        context['todays_events'] = Event.objects.filter(date=today).select_related('category').prefetch_related('participants')
        context['event_form'] = EventForm()
        context['participant_form'] = ParticipantForm()
        context['category_form'] = self.get_form()  # Use the form instance being edited
        context['editing_category'] = True  # Flag to show we're editing
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Category updated successfully!')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error updating category. Please check the form.')
        return super().form_invalid(form)

class CategoryDeleteView(DeleteView):
    model = Category
    success_url = reverse_lazy('events:dashboard')
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object() #Delete Category
        self.object.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect(self.success_url)
