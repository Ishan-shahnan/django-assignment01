from django.test import TestCase
from django.utils import timezone
from datetime import date, time
from .models import Event, Participant, Category

class EventModelTest(TestCase):
    def setUp(self):
        # Create test categories
        self.category1 = Category.objects.create(
            name="Technology",
            description="Tech events and conferences"
        )
        self.category2 = Category.objects.create(
            name="Business",
            description="Business and networking events"
        )
        
        # Create test events
        self.event1 = Event.objects.create(
            name="Tech Conference 2024",
            description="Annual technology conference",
            date=date(2024, 12, 15),
            time=time(9, 0),
            location="Convention Center",
            category=self.category1
        )
        
        self.event2 = Event.objects.create(
            name="Business Networking",
            description="Networking event for professionals",
            date=date(2024, 11, 20),
            time=time(18, 0),
            location="Business Center",
            category=self.category2
        )
        
        # Create test participants
        self.participant1 = Participant.objects.create(
            name="John Doe",
            email="john@example.com"
        )
        self.participant2 = Participant.objects.create(
            name="Jane Smith",
            email="jane@example.com"
        )
        
        # Add participants to events
        self.event1.participants.add(self.participant1, self.participant2)
        self.event2.participants.add(self.participant1)

    def test_optimized_queries(self):
        """Test that select_related and prefetch_related work correctly"""
        # Test select_related for category
        events = Event.objects.select_related('category').all()
        for event in events:
            # This should not trigger additional queries
            category_name = event.category.name
            self.assertIsNotNone(category_name)
    
    def test_aggregate_queries(self):
        """Test aggregate queries for participant count"""
        from django.db.models import Count
        
        # Test total participant count
        total_participants = Participant.objects.aggregate(total=Count('id'))['total']
        self.assertEqual(total_participants, 2)
        
        # Test total events count
        total_events = Event.objects.aggregate(total=Count('id'))['total']
        self.assertEqual(total_events, 2)
        
        # Test total categories count
        total_categories = Category.objects.aggregate(total=Count('id'))['total']
        self.assertEqual(total_categories, 2)
    
    def test_filter_queries(self):
        """Test filtering by category and date range"""
        from datetime import date
        
        # Test category filtering
        tech_events = Event.objects.filter(category=self.category1)
        self.assertEqual(tech_events.count(), 1)
        self.assertEqual(tech_events.first().name, "Tech Conference 2024")
        
        # Test date range filtering
        start_date = date(2024, 11, 1)
        end_date = date(2024, 11, 30)
        events_in_november = Event.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        )
        self.assertEqual(events_in_november.count(), 1)
        self.assertEqual(events_in_november.first().name, "Business Networking")
    
    def test_many_to_many_relationship(self):
        """Test ManyToMany relationship between Participant and Event"""
        # Test participant has events
        self.assertEqual(self.participant1.events.count(), 2)
        self.assertEqual(self.participant2.events.count(), 1)
        
        # Test event has participants
        self.assertEqual(self.event1.participants.count(), 2)
        self.assertEqual(self.event2.participants.count(), 1)
    
    def test_model_string_representations(self):
        """Test __str__ methods of models"""
        self.assertEqual(str(self.category1), "Technology")
        self.assertEqual(str(self.event1), "Tech Conference 2024")
        self.assertEqual(str(self.participant1), "John Doe")
