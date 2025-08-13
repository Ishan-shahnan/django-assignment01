from datetime import date

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.db.models import Q, Count
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin

from users.models import CustomUser
from .decorators import group_required
from .forms import EventForm, ParticipantForm, CategoryForm, SignUpForm, SignInForm, AssignRoleForm, CreateGroupForm
from .models import Event, Participant, Category, RSVP


# home-page
class HomeView(TemplateView):
    template_name = 'events/event_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()

        # upcoming
        context['upcoming_events'] = Event.objects.select_related('category').prefetch_related('participants').filter(
            date__gte=today).order_by('date', 'time')[:6]

        # previous
        context['previous_events'] = Event.objects.select_related('category').prefetch_related('participants').filter(
            date__lt=today).order_by('-date', 'time')[:6]

        # search
        context['categories'] = Category.objects.all()

        context['total_participants'] = Participant.objects.aggregate(total=Count('id'))['total']

        return context


# event
class EventsView(ListView):
    model = Event
    template_name = 'events/events.html'
    context_object_name = 'events'

    def get_queryset(self):

        queryset = Event.objects.select_related('category').prefetch_related('participants')

        #search
        search = self.request.GET.get('search')
        category = self.request.GET.get('category')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if any([search, category, start_date, end_date]):
            print(
                f"Search params - search: '{search}', category: '{category}', start: '{start_date}', end: '{end_date}'")

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

        #Tot-participants
        context['total_participants'] = Participant.objects.aggregate(total=Count('id'))['total']

        return context


# contact-page
class ContactView(TemplateView):
    template_name = 'events/contact.html'


# dashboard-page
@method_decorator(group_required('Admin', 'Organizer'), name='dispatch')
class DashboardView(TemplateView):
    template_name = 'events/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()

        context['events'] = Event.objects.select_related('category').prefetch_related('participants').all().order_by(
            '-date', '-time')
        context['participants'] = Participant.objects.prefetch_related('events').all()
        context['categories'] = Category.objects.all()

        context['total_participants'] = Participant.objects.aggregate(total=Count('id'))['total']
        context['total_events'] = Event.objects.aggregate(total=Count('id'))['total']
        context['total_categories'] = Category.objects.aggregate(total=Count('id'))['total']

        context['upcoming_events_count'] = Event.objects.filter(date__gte=today).count()
        context['past_events_count'] = Event.objects.filter(date__lt=today).count()

        context['todays_events'] = Event.objects.select_related('category').prefetch_related('participants').filter(
            date=today).order_by('time')

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
                # error-log event
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
                # error-log participant
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
                print("Category form errors:", form.errors)
                error_message = "Error creating category. Please check the form."
                if form.errors:
                    error_details = []
                    for field, errors in form.errors.items():
                        field_name = field.replace('_', ' ').title()
                        error_details.append(f"{field_name}: {', '.join(errors)}")
                    error_message += f" Errors: {', '.join(error_details)}"
                messages.error(request, error_message)

        return redirect('dashboard')


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        return Event.objects.select_related('category').prefetch_related('participants')


#CRUD
@method_decorator(group_required('Admin', 'Organizer'), name='dispatch')
class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/dashboard.html'
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        context['events'] = Event.objects.select_related('category').prefetch_related('participants').all().order_by(
            '-date', '-time')
        context['participants'] = Participant.objects.prefetch_related('events').all()
        context['categories'] = Category.objects.all()
        context['total_participants'] = Participant.objects.aggregate(total=Count('id'))['total']
        context['total_events'] = Event.objects.aggregate(total=Count('id'))['total']
        context['total_categories'] = Category.objects.aggregate(total=Count('id'))['total']
        context['upcoming_events_count'] = Event.objects.filter(date__gte=today).count()
        context['past_events_count'] = Event.objects.filter(date__lt=today).count()
        context['todays_events'] = Event.objects.filter(date=today).select_related('category').prefetch_related(
            'participants')
        context['event_form'] = EventForm()
        context['participant_form'] = ParticipantForm()
        context['category_form'] = CategoryForm()
        context['image_field'] = getattr(Event, 'image', None)
        return context

    def form_valid(self, form):
        if 'image' in self.request.FILES:
            form.instance.image = self.request.FILES['image']
        response = super().form_valid(form)
        messages.success(self.request, 'Event created successfully!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Error creating event. Please check the form.')
        return super().form_invalid(form)


@method_decorator(group_required('Admin', 'Organizer'), name='dispatch')
class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/dashboard.html'
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today() 
        context['events'] = Event.objects.select_related('category').prefetch_related('participants').all().order_by(
            '-date', '-time')
        context['participants'] = Participant.objects.prefetch_related('events').all()
        context['categories'] = Category.objects.all()
        context['total_participants'] = Participant.objects.aggregate(total=Count('id'))['total']
        context['total_events'] = Event.objects.aggregate(total=Count('id'))['total']
        context['total_categories'] = Category.objects.aggregate(total=Count('id'))['total']
        context['upcoming_events_count'] = Event.objects.filter(date__gte=today).count()
        context['past_events_count'] = Event.objects.filter(date__lt=today).count()
        context['todays_events'] = Event.objects.filter(date=today).select_related('category').prefetch_related(
            'participants')
        context['event_form'] = self.get_form() 
        context['participant_form'] = ParticipantForm()
        context['category_form'] = CategoryForm()
        context['editing_event'] = True
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


@method_decorator(group_required('Admin'), name='dispatch')
class EventDeleteView(DeleteView):
    model = Event
    success_url = reverse_lazy('dashboard')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect(self.success_url)


class ParticipantCreateView(CreateView):
    model = Participant
    form_class = ParticipantForm
    template_name = 'events/dashboard.html'
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        context['events'] = Event.objects.select_related('category').prefetch_related('participants').all().order_by(
            '-date', '-time')
        context['participants'] = Participant.objects.prefetch_related('events').all()
        context['categories'] = Category.objects.all()
        context['total_participants'] = Participant.objects.aggregate(total=Count('id'))['total']
        context['total_events'] = Event.objects.aggregate(total=Count('id'))['total']
        context['total_categories'] = Category.objects.aggregate(total=Count('id'))['total']
        context['upcoming_events_count'] = Event.objects.filter(date__gte=today).count()
        context['past_events_count'] = Event.objects.filter(date__lt=today).count()
        context['todays_events'] = Event.objects.filter(date=today).select_related('category').prefetch_related(
            'participants')
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
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        context['events'] = Event.objects.select_related('category').prefetch_related('participants').all().order_by(
            '-date', '-time')
        context['participants'] = Participant.objects.prefetch_related('events').all()
        context['categories'] = Category.objects.all()
        context['total_participants'] = Participant.objects.aggregate(total=Count('id'))['total']
        context['total_events'] = Event.objects.aggregate(total=Count('id'))['total']
        context['total_categories'] = Category.objects.aggregate(total=Count('id'))['total']
        context['upcoming_events_count'] = Event.objects.filter(date__gte=today).count()
        context['past_events_count'] = Event.objects.filter(date__lt=today).count()
        context['todays_events'] = Event.objects.filter(date=today).select_related('category').prefetch_related(
            'participants')
        context['event_form'] = EventForm()
        context['participant_form'] = self.get_form()
        context['category_form'] = CategoryForm()
        context['editing_participant'] = True 
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
    success_url = reverse_lazy('dashboard')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(request, 'Participant deleted successfully!')
        return redirect(self.success_url)



@method_decorator(group_required('Admin', 'Organizer'), name='dispatch')
class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'events/dashboard.html'
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today() 
        context['events'] = Event.objects.select_related('category').prefetch_related('participants').all().order_by(
            '-date', '-time')
        context['participants'] = Participant.objects.prefetch_related('events').all()
        context['categories'] = Category.objects.all()
        context['total_participants'] = Participant.objects.aggregate(total=Count('id'))['total']
        context['total_events'] = Event.objects.aggregate(total=Count('id'))['total']
        context['total_categories'] = Category.objects.aggregate(total=Count('id'))['total']
        context['upcoming_events_count'] = Event.objects.filter(date__gte=today).count()
        context['past_events_count'] = Event.objects.filter(date__lt=today).count()
        context['todays_events'] = Event.objects.filter(date=today).select_related('category').prefetch_related(
            'participants')
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


@method_decorator(group_required('Admin', 'Organizer'), name='dispatch')
class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'events/dashboard.html'
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        context['events'] = Event.objects.select_related('category').prefetch_related('participants').all().order_by(
            '-date', '-time')
        context['participants'] = Participant.objects.prefetch_related('events').all()
        context['categories'] = Category.objects.all()
        context['total_participants'] = Participant.objects.aggregate(total=Count('id'))['total']
        context['total_events'] = Event.objects.aggregate(total=Count('id'))['total']
        context['total_categories'] = Category.objects.aggregate(total=Count('id'))['total']
        context['upcoming_events_count'] = Event.objects.filter(date__gte=today).count()
        context['past_events_count'] = Event.objects.filter(date__lt=today).count()
        context['todays_events'] = Event.objects.filter(date=today).select_related('category').prefetch_related(
            'participants')
        context['event_form'] = EventForm()
        context['participant_form'] = ParticipantForm()
        context['category_form'] = self.get_form() 
        context['editing_category'] = True
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


@method_decorator(group_required('Admin'), name='dispatch')
class CategoryDeleteView(DeleteView):
    model = Category
    success_url = reverse_lazy('dashboard')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect(self.success_url)


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'events/signup.html'
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        return render(self.request, 'events/activation_sent.html')
    
    def form_invalid(self, form):
        return super().form_invalid(form)


class ActivateView(View):
    def get(self, request, user_id, token):
        try:
            user = CustomUser.objects.get(id=user_id)
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                participant_group, created = Group.objects.get_or_create(name='Participant')
                user.groups.add(participant_group)
                login(request, user)
                messages.success(request, 'Account activated successfully!')
                return redirect('dashboard-redirect')
            else:
                messages.error(request, 'Invalid activation link.')
                return render(request, 'events/activation_invalid.html')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return render(request, 'events/activation_invalid.html')


class CustomLoginView(LoginView):
    template_name = 'events/login.html'
    form_class = SignInForm

    def get_success_url(self):
        return reverse_lazy('dashboard-redirect')


class DashboardRedirectView(LoginRequiredMixin, View):
    login_url = 'sign-in'
    
    def get(self, request):
        user_groups = request.user.groups.values_list('name', flat=True)
        if 'Admin' in user_groups:
            return redirect('admin-dashboard')
        elif 'Organizer' in user_groups:
            return redirect('organizer-dashboard')
        elif 'Participant' in user_groups:
            return redirect('participant-dashboard')
        else:
            messages.error(request, 'No role assigned. Please contact the administrator.')
            return redirect('sign-in')


class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'events/admin_dashboard.html'
    login_url = 'sign-in'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Admin').exists():
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard-redirect')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        context.update({
            'events': Event.objects.select_related('category').prefetch_related('participants').all().order_by('-date', '-time'),
            'participants': Participant.objects.prefetch_related('events').all(),
            'categories': Category.objects.all(),
            'total_participants': Participant.objects.aggregate(total=Count('id'))['total'],
            'total_events': Event.objects.aggregate(total=Count('id'))['total'],
            'total_categories': Category.objects.aggregate(total=Count('id'))['total'],
            'upcoming_events_count': Event.objects.filter(date__gte=today).count(),
            'past_events_count': Event.objects.filter(date__lt=today).count(),
            'todays_events': Event.objects.filter(date=today).select_related('category').prefetch_related('participants'),
            'event_form': EventForm(),
            'participant_form': ParticipantForm(),
            'category_form': CategoryForm()
        })
        return context


class OrganizerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'events/organizer_dashboard.html'
    login_url = 'sign-in'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Organizer').exists():
            messages.error(request, 'Access denied. Organizer privileges required.')
            return redirect('dashboard-redirect')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        context.update({
            'events': Event.objects.select_related('category').prefetch_related('participants').all().order_by('-date', '-time'),
            'organized_events': Event.objects.select_related('category').prefetch_related('participants').all().order_by('-date', '-time'),
            'participants': Participant.objects.prefetch_related('events').all(),
            'categories': Category.objects.all(),
            'total_participants': Participant.objects.aggregate(total=Count('id'))['total'],
            'total_events': Event.objects.aggregate(total=Count('id'))['total'],
            'total_categories': Category.objects.aggregate(total=Count('id'))['total'],
            'upcoming_events_count': Event.objects.filter(date__gte=today).count(),
            'past_events_count': Event.objects.filter(date__lt=today).count(),
            'todays_events': Event.objects.filter(date=today).select_related('category').prefetch_related('participants'),
            'event_form': EventForm(),
            'participant_form': ParticipantForm(),
            'category_form': CategoryForm()
        })
        return context


class ParticipantDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'events/participant_dashboard.html'
    login_url = 'sign-in'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name__in=['Participant', 'Admin']).exists():
            messages.error(request, 'Access denied.')
            return redirect('dashboard-redirect')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rsvp_events'] = self.request.user.rsvp_events.all()
        return context


class RSVPEventView(LoginRequiredMixin, View):
    login_url = 'sign-in'
    
    def post(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        
        if event.is_past:
            messages.error(request, 'Cannot RSVP to past events.')
            return redirect('event-detail', pk=event_id)
        
        existing_confirmed_rsvp = RSVP.objects.filter(event=event, status='confirmed').first()
        if existing_confirmed_rsvp and existing_confirmed_rsvp.user != request.user:
            messages.error(request, 'This event already has a confirmed RSVP. Only one person can RSVP per event.')
            return redirect('event-detail', pk=event_id)
        
        existing_rsvp = RSVP.objects.filter(user=request.user, event=event).first()
        
        if existing_rsvp:
            if existing_rsvp.status == 'confirmed':
                existing_rsvp.status = 'cancelled'
                existing_rsvp.save()
                event.rsvps.remove(request.user)
                messages.success(request, 'You have successfully cancelled your RSVP.')
            else:
                existing_rsvp.status = 'confirmed'
                existing_rsvp.save()
                event.rsvps.add(request.user)
                messages.success(request, 'You have successfully RSVP\'d for this event! A confirmation email has been sent to your registered email address.')
        else:
            try:
                rsvp = RSVP.objects.create(
                    user=request.user,
                    event=event,
                    status='confirmed'
                )
                event.rsvps.add(request.user)
                participant, created = Participant.objects.get_or_create(
                    name=request.user.get_full_name() or request.user.username,
                    email=request.user.email,
                    defaults={
                        'name': request.user.get_full_name() or request.user.username,
                        'email': request.user.email
                    }
                )
                
                participant.events.add(event)
                
                messages.success(request, 'You have successfully RSVP\'d for this event and been added as a participant! A confirmation email has been sent to your registered email address.')
            except Exception as e:
                messages.error(request, 'An error occurred while processing your RSVP. Please try again.')

        return redirect('event-detail', pk=event_id)
    
    def get(self, request, event_id):
        return redirect('event-detail', pk=event_id)


class MyRSVPsView(LoginRequiredMixin, ListView):
    template_name = 'events/my_rsvps.html'
    context_object_name = 'rsvps'
    login_url = 'sign-in'
    
    def get_queryset(self):
        return RSVP.objects.filter(
            user=self.request.user, 
            status='confirmed'
        ).select_related('event', 'event__category').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_rsvps'] = self.get_queryset().count()
        return context


class ManageRSVPsView(LoginRequiredMixin, ListView):
    template_name = 'events/manage_rsvps.html'
    context_object_name = 'rsvps'
    login_url = 'sign-in'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name__in=['Admin', 'Organizer']).exists():
            messages.error(request, 'Access denied. Admin or Organizer privileges required.')
            return redirect('dashboard-redirect')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return RSVP.objects.select_related('user', 'event', 'event__category').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context.update({
            'total_rsvps': queryset.count(),
            'confirmed_rsvps': queryset.filter(status='confirmed').count(),
            'cancelled_rsvps': queryset.filter(status='cancelled').count(),
        })
        return context


class EventRSVPsView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'events/event_rsvps.html'
    context_object_name = 'event'
    login_url = 'sign-in'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name__in=['Admin', 'Organizer']).exists():
            messages.error(request, 'Access denied. Admin or Organizer privileges required.')
            return redirect('dashboard-redirect')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rsvps = RSVP.objects.filter(event=self.object).select_related('user').order_by('-created_at')
        context.update({
            'rsvps': rsvps,
            'confirmed_rsvps': rsvps.filter(status='confirmed'),
            'cancelled_rsvps': rsvps.filter(status='cancelled'),
            'total_rsvps': rsvps.filter(status='confirmed').count(),
        })
        return context


class DeleteRSVPView(LoginRequiredMixin, DeleteView):
    model = RSVP
    success_url = reverse_lazy('manage-rsvps')
    login_url = 'sign-in'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name__in=['Admin', 'Organizer']).exists():
            messages.error(request, 'Access denied. Admin or Organizer privileges required.')
            return redirect('dashboard-redirect')
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self, queryset=None):
        """Override to use rsvp_id instead of pk"""
        rsvp_id = self.kwargs.get('rsvp_id')
        if rsvp_id is None:
            raise AttributeError("Generic detail view %s must be called with either an object pk or a slug in the URLconf." % self.__class__.__name__)
        return get_object_or_404(RSVP, id=rsvp_id)
    
    def get(self, request, *args, **kwargs):
        rsvp = self.get_object()
        event_id = rsvp.event.id
        user = rsvp.user
        
        rsvp.event.rsvps.remove(user)
        rsvp.delete()
        
        messages.success(request, f'RSVP for {user.username} has been removed.')
        return redirect('event-rsvps', event_id=event_id)


class RBACDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'events/rbac_dashboard.html'
    login_url = 'sign-in'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Admin').exists():
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard-redirect')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = CustomUser.objects.select_related().prefetch_related('groups').all()
        groups = Group.objects.all()
        
        # Role info
        for user in users:
            user_groups = user.groups.all()
            if user_groups:
                user.current_role = user_groups[0].name
            else:
                user.current_role = 'No Role'
        
        context.update({
            'users': users,
            'groups': groups,
            'assign_role_form': AssignRoleForm(),
            'create_group_form': CreateGroupForm(),
        })
        return context


class AssignUserRoleView(LoginRequiredMixin, View):
    login_url = 'sign-in'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Admin').exists():
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard-redirect')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        form = AssignRoleForm(request.POST)
        
        if form.is_valid():
            role_name = form.cleaned_data['role']
            
            try:
                role_group, created = Group.objects.get_or_create(name=role_name)
                
                user.groups.clear()
                user.groups.add(role_group)
                
                messages.success(request, f'Successfully assigned {role_name} role to {user.username}')
                
            except Exception as e:
                messages.error(request, f'Error assigning role: {str(e)}')
        else:
            messages.error(request, 'Please select a valid role')
        
        return redirect('rbac-dashboard')


class CreateGroupView(LoginRequiredMixin, View):
    login_url = 'sign-in'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Admin').exists():
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard-redirect')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        form = CreateGroupForm(request.POST)
        
        if form.is_valid():
            group_name = form.cleaned_data['name']
            
            try:
                Group.objects.create(name=group_name)
                messages.success(request, f'Successfully created group: {group_name}')
            except Exception as e:
                messages.error(request, f'Error creating group: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
        
        return redirect('rbac-dashboard')


class DeleteGroupView(LoginRequiredMixin, DeleteView):
    model = Group
    success_url = reverse_lazy('rbac-dashboard')
    login_url = 'sign-in'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Admin').exists():
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard-redirect')
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self, queryset=None):
        """Override to use group_id instead of pk"""
        group_id = self.kwargs.get('group_id')
        if group_id is None:
            raise AttributeError("Generic detail view %s must be called with either an object pk or a slug in the URLconf." % self.__class__.__name__)
        return get_object_or_404(Group, id=group_id)
    
    def get(self, request, *args, **kwargs):
        group = self.get_object()
        
        core_groups = ['Admin', 'Organizer', 'Participant']
        if group.name in core_groups:
            messages.error(request, f'Cannot delete core group: {group.name}')
        else:
            group_name = group.name
            group.delete()
            messages.success(request, f'Successfully deleted group: {group_name}')
        
        return redirect(self.success_url)


class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = User
    success_url = reverse_lazy('rbac-dashboard')
    login_url = 'sign-in'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Admin').exists():
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard-redirect')
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self, queryset=None):
        """Override to use user_id instead of pk"""
        user_id = self.kwargs.get('user_id')
        if user_id is None:
            raise AttributeError("Generic detail view %s must be called with either an object pk or a slug in the URLconf." % self.__class__.__name__)
        return get_object_or_404(User, id=user_id)
    
    def get(self, request, *args, **kwargs):
        user = self.get_object()
        
        if user == request.user:
            messages.error(request, 'Cannot delete your own account')
        elif user.is_superuser:
            messages.error(request, 'Cannot delete superuser accounts')
        else:
            username = user.username
            user.delete()
            messages.success(request, f'Successfully deleted user: {username}')
        
        return redirect(self.success_url)
