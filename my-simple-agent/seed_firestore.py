import datetime
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-01-995125327448"

def seed_database():
    print(f"Connecting to Firestore for project: {PROJECT_ID}")
    db = firestore.Client(project=PROJECT_ID, database="(default)")
    palettes_ref = db.collection("palettes")

    sample_palettes = [
        {
            "id": "ocean-breeze",
            "name": "Ocean Breeze UI",
            "category": "UI Theme",
            "colors": ["#0f172a", "#0284c7", "#38bdf8", "#f8fafc"],
            "primary_color": "#0284c7",
            "background_color": "#0f172a",
            "contrast_ratio": 7.42,
            "tags": ["modern", "dark-mode", "accessible"],
            "description": "Deep ocean slate background with vibrant sky blue accents.",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
        {
            "id": "emerald-forest",
            "name": "Emerald Forest",
            "category": "Branding",
            "colors": ["#064e3b", "#059669", "#34d399", "#ecfdf5"],
            "primary_color": "#059669",
            "background_color": "#ecfdf5",
            "contrast_ratio": 4.85,
            "tags": ["nature", "fresh", "light-mode"],
            "description": "Lush botanical greens on a crisp, clean light backdrop.",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
        {
            "id": "sunset-synthwave",
            "name": "Sunset Synthwave",
            "category": "Creative",
            "colors": ["#181825", "#f43f5e", "#fb923c", "#fde047"],
            "primary_color": "#f43f5e",
            "background_color": "#181825",
            "contrast_ratio": 5.12,
            "tags": ["retro", "vibrant", "dark-mode"],
            "description": "High-energy 80s neon gradient theme for creative apps.",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
        {
            "id": "minimalist-slate",
            "name": "Minimalist Slate",
            "category": "Accessibility Focus",
            "colors": ["#1e293b", "#475569", "#94a3b8", "#ffffff"],
            "primary_color": "#1e293b",
            "background_color": "#ffffff",
            "contrast_ratio": 12.6,
            "tags": ["high-contrast", "accessible", "minimal"],
            "description": "Ultra high contrast slate and monochrome theme exceeding WCAG AAA standards.",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
    ]

    for item in sample_palettes:
        doc_ref = palettes_ref.document(item["id"])
        doc_ref.set(item)
        print(f"Seeded palette: {item['name']} ({item['id']})")

if __name__ == "__main__":
    seed_database()
