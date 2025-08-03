import os
import sys
import django
from datetime import date, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from faker import Faker
from events.models import Event, Participant, Category


fake = Faker()

def create_categories():
    """Create event categories"""
    categories_data = [
        {'name': 'Wedding', 'description': 'Beautiful wedding ceremonies and celebrations'},
        {'name': 'Sports', 'description': 'Sports events, tournaments, and athletic competitions'},
        {'name': 'Conference', 'description': 'Professional conferences and business meetings'},
        {'name': 'Campus', 'description': 'University and campus events'},
        {'name': 'Technology', 'description': 'Tech events, hackathons, and innovation workshops'},
        {'name': 'Music', 'description': 'Concerts, music festivals, and performances'},
        {'name': 'Food & Dining', 'description': 'Food festivals, cooking classes, and dining events'},
        {'name': 'Art & Culture', 'description': 'Art exhibitions, cultural events, and workshops'},
        {'name': 'Health & Wellness', 'description': 'Fitness events, wellness workshops, and health seminars'},
        {'name': 'Education', 'description': 'Educational workshops, seminars, and training programs'}
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        categories.append(category)
        if created:
            print(f"✅ Created category: {category.name}")
        else:
            print(f"📝 Category already exists: {category.name}")
    
    return categories

def create_events(categories):
    """Create realistic events using Faker"""
    event_templates = [
        
        {
            'name_template': '{} Wedding',
            'description_template': 'A beautiful celebration of love and commitment. {}',
            'location_template': '{} Wedding Venue',
            'category_name': 'Wedding',
            'time_range': (16, 20),  
            'date_range': (30, 365),  
            'description_variations': [
                'Join us for an elegant ceremony and reception.',
                'A romantic celebration of two hearts becoming one.',
                'An intimate gathering of family and friends.',
                'A dream wedding with all the magical moments.'
            ]
        },
        
        {
            'name_template': '{} Tournament',
            'description_template': 'Exciting sports competition featuring top athletes. {}',
            'location_template': '{} Stadium',
            'category_name': 'Sports',
            'time_range': (9, 18),  
            'date_range': (7, 180), 
            'description_variations': [
                'Competitive tournament with prizes and recognition.',
                'Showcase of athletic talent and sportsmanship.',
                'High-energy competition for all skill levels.',
                'Championship event with professional standards.'
            ]
        },
        
        {
            'name_template': '{} Conference',
            'description_template': 'Professional conference bringing together industry experts. {}',
            'location_template': '{} Convention Center',
            'category_name': 'Conference',
            'time_range': (8, 17),  
            'date_range': (14, 120), 
            'description_variations': [
                'Networking opportunities with industry leaders.',
                'Insights and innovations from thought leaders.',
                'Professional development and knowledge sharing.',
                'Cutting-edge presentations and workshops.'
            ]
        },
        
        {
            'name_template': '{} Campus Event',
            'description_template': 'University campus event for students and faculty. {}',
            'location_template': '{} University Campus',
            'category_name': 'Campus',
            'time_range': (10, 16), 
            'date_range': (7, 90), 
            'description_variations': [
                'Student-focused activities and learning opportunities.',
                'Academic and social events for the campus community.',
                'Educational workshops and skill development.',
                'Campus culture and community building.'
            ]
        },
        
        {
            'name_template': '{} Tech Meetup',
            'description_template': 'Technology-focused event for developers and tech enthusiasts. {}',
            'location_template': '{} Tech Hub',
            'category_name': 'Technology',
            'time_range': (18, 21),
            'date_range': (7, 60),
            'description_variations': [
                'Latest trends in technology and innovation.',
                'Hands-on workshops and coding sessions.',
                'Networking with tech professionals and startups.',
                'Showcase of cutting-edge technologies.'
            ]
        },
        
        {
            'name_template': '{} Music Festival',
            'description_template': 'Amazing musical performances and entertainment. {}',
            'location_template': '{} Music Hall',
            'category_name': 'Music',
            'time_range': (19, 23), 
            'date_range': (14, 180),
            'description_variations': [
                'Live performances by talented artists.',
                'Diverse musical genres and entertainment.',
                'Unforgettable musical experiences and memories.',
                'Celebration of music and cultural diversity.'
            ]
        },
        
        {
            'name_template': '{} Food Festival',
            'description_template': 'Culinary delights and gastronomic experiences. {}',
            'location_template': '{} Food Court',
            'category_name': 'Food & Dining',
            'time_range': (11, 20),
            'date_range': (7, 90),
            'description_variations': [
                'Taste delicious cuisines from around the world.',
                'Cooking demonstrations and food workshops.',
                'Celebration of culinary arts and culture.',
                'Gourmet experiences and food networking.'
            ]
        },
        
        {
            'name_template': '{} Art Exhibition',
            'description_template': 'Creative showcase of artistic talent and expression. {}',
            'location_template': '{} Art Gallery',
            'category_name': 'Art & Culture',
            'time_range': (10, 18),
            'date_range': (7, 120), 
            'description_variations': [
                'Contemporary art from emerging and established artists.',
                'Cultural exhibitions and artistic workshops.',
                'Creative expression and artistic inspiration.',
                'Diverse art forms and cultural experiences.'
            ]
        },
       
        {
            'name_template': '{} Wellness Workshop',
            'description_template': 'Health and wellness focused activities and education. {}',
            'location_template': '{} Wellness Center',
            'category_name': 'Health & Wellness',
            'time_range': (9, 17), 
            'date_range': (7, 60), 
            'description_variations': [
                'Fitness workshops and wellness education.',
                'Healthy lifestyle tips and practices.',
                'Mind-body wellness and stress management.',
                'Professional health and fitness guidance.'
            ]
        },
       
        {
            'name_template': '{} Learning Workshop',
            'description_template': 'Educational workshops and skill development sessions. {}',
            'location_template': '{} Learning Center',
            'category_name': 'Education',
            'time_range': (9, 16),  
            'date_range': (7, 90), 
            'description_variations': [
                'Professional development and skill enhancement.',
                'Interactive learning and knowledge sharing.',
                'Educational workshops for all skill levels.',
                'Lifelong learning and personal growth.'
            ]
        }
    ]
    
    events_created = 0
    for template in event_templates:
        category = next((cat for cat in categories if cat.name == template['category_name']), None)
        if not category:
            continue
            
        
        num_events = random.randint(3, 5)
        for i in range(num_events):
            
            event_name = template['name_template'].format(fake.word().title())
            event_description = template['description_template'].format(
                random.choice(template['description_variations'])
            )
            event_location = template['location_template'].format(fake.city())
            
            
            days_from_now = random.randint(*template['date_range'])
            event_date = date.today() + timedelta(days=days_from_now)
            
            
            hour = random.randint(*template['time_range'])
            minute = random.choice([0, 15, 30, 45])
            event_time = f"{hour:02d}:{minute:02d}"
            
            
            event, created = Event.objects.get_or_create(
                name=event_name,
                defaults={
                    'description': event_description,
                    'date': event_date,
                    'time': event_time,
                    'location': event_location,
                    'category': category
                }
            )
            
            if created:
                events_created += 1
                print(f"✅ Created event: {event.name} on {event.date}")
    
    return events_created

def create_participants(events):
    """Create realistic participants and assign them to events"""
    participants_created = 0
    
    
    for event in events:
        
        num_participants = random.randint(2, 6)
        
        for i in range(num_participants):
            
            participant_name = fake.name()
            participant_email = fake.email()
            
           
            participant, created = Participant.objects.get_or_create(
                email=participant_email,
                defaults={'name': participant_name}
            )
            
            
            if event not in participant.events.all():
                participant.events.add(event)
                participants_created += 1
                if created:
                    print(f"✅ Created participant: {participant.name} ({participant.email})")
                else:
                    print(f"📝 Added existing participant: {participant.name} to {event.name}")
    
    return participants_created

def main():
    print("🎉 Starting Database Population with Faker")
    print("=" * 60)
    
    
    print("\n🗑️  Clearing existing data...")
    Event.objects.all().delete()
    Participant.objects.all().delete()
    Category.objects.all().delete()
    print("✅ Existing data cleared")
    
    
    print("\n📂 Creating categories...")
    categories = create_categories()
    print(f"✅ Created {len(categories)} categories")
    
    
    print("\n📅 Creating events...")
    events_created = create_events(categories)
    print(f"✅ Created {events_created} events")
    
    
    all_events = Event.objects.all()
    
    
    print("\n👥 Creating participants...")
    participants_created = create_participants(all_events)
    print(f"✅ Created {participants_created} participant-event relationships")
    
   
    print("\n" + "=" * 60)
    print("📊 FINAL SUMMARY:")
    print(f"   • Categories: {Category.objects.count()}")
    print(f"   • Events: {Event.objects.count()}")
    print(f"   • Participants: {Participant.objects.count()}")
    print(f"   • Total participant-event relationships: {sum([e.participants.count() for e in Event.objects.all()])}")
    
    
    print(f"\n📋 SAMPLE DATA:")
    print("Categories:")
    for cat in Category.objects.all()[:5]:
        print(f"   • {cat.name}")
    
    print("\nEvents:")
    for event in Event.objects.all()[:5]:
        print(f"   • {event.name} ({event.date}) - {event.participants.count()} participants")
    
    print("\nParticipants:")
    for participant in Participant.objects.all()[:5]:
        print(f"   • {participant.name} ({participant.email}) - {participant.events.count()} events")
    
    print("=" * 60)
    print("🎉 Database population completed successfully!")

if __name__ == '__main__':
    main() 