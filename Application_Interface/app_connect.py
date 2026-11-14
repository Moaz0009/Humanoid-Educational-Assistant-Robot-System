import firebase_admin
from firebase_admin import credentials, db
import json

# Service Account file path
SERVICE_ACCOUNT_PATH = r"future-app2-firebase-adminsdk-fbsvc-da6bf73623.json"

def initialize_and_get_data():
    """Initialize Firebase and get all children data"""
    try:
        # Initialize Firebase if not already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://future-app2-default-rtdb.firebaseio.com/'
            })
            print("✓ Firebase initialized successfully!")
        else:
            print("✓ Firebase already initialized")
        
        # Get data from Firebase
        ref = db.reference('children')
        data = ref.get()
        
        if not data:
            print("No data found in database")
            return []
        
        extracted_data = []
        
        for child_id, child_data in data.items():
            child_info = {
                'id': child_id,
                'name': child_data.get('name', ''),
                'performance': child_data.get('performance', ''),
                'questions': child_data.get('questions', {}),
                'correctAnswers': child_data.get('correctAnswers', {}),
                'comments': child_data.get('comments', ''),
                'exams': child_data.get('exams', ''),
                'parentEmail': child_data.get('parentEmail', ''),
                'parentID': child_data.get('parentID', '')
            }
            extracted_data.append(child_info)
        
        print(f"✓ Data loaded successfully - {len(extracted_data)} children found")
        return extracted_data
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return []

def find_child_by_name(data, name):
    """Find child by name (exact or partial match)"""
    name_lower = name.lower().strip()
    
    if not name_lower:
        return None
    
    # First try exact match
    for child in data:
        if child['name'].lower().strip() == name_lower:
            return child
    
    # If no exact match, try partial match
    matches = []
    for child in data:
        if name_lower in child['name'].lower().strip():
            matches.append(child)
    
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        print(f"\n⚠️ Multiple children found with name '{name}':")
        for i, child in enumerate(matches, 1):
            print(f"{i}. {child['name']} (ID: {child['id']})")
        
        try:
            choice = int(input("Choose child number: ")) - 1
            if 0 <= choice < len(matches):
                return matches[choice]
            else:
                print("Invalid choice")
                return None
        except ValueError:
            print("Please enter a valid number")
            return None
    
    return None


def update_performance(data, child_name, new_performance):
    """Update child's performance in Firebase"""
    try:
        child = find_child_by_name(data, child_name)
        if not child:
            print(f"❌ Child '{child_name}' not found")
            return False
        
        # Update in Firebase
        ref = db.reference(f'children/{child["id"]}/performance')
        ref.set(new_performance)
        
        # Update in local data
        child['performance'] = new_performance
        
        print(f"✓ Performance updated successfully for {child['name']}")
        print(f"New performance: {new_performance}")
        return True
        
    except Exception as e:
        print(f"✗ Error updating performance: {e}")
        return False