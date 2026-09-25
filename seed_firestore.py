"""Seed script for initializing the Firestore database for GlobeTrotter AI (Travel Planner).

Hardcoded project ID: qwiklabs-gcp-01-84b0d8af1726
"""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-01-84b0d8af1726"

SAMPLE_DESTINATIONS = [
    {
        "id": "kyoto_japan",
        "name": "Kyoto, Japan",
        "category": "Culture & History",
        "country": "Japan",
        "estimated_cost_per_day": 180,
        "best_season": "Spring / Autumn",
        "description": "Famed for its classical Buddhist temples, gardens, imperial palaces, Shinto shrines, and traditional wooden houses.",
        "rating": 4.9,
    },
    {
        "id": "paris_france",
        "name": "Paris, France",
        "category": "Romance & Art",
        "country": "France",
        "estimated_cost_per_day": 250,
        "best_season": "Spring / Summer",
        "description": "Global center for art, fashion, gastronomy, and culture, featuring iconic landmarks like the Eiffel Tower and Louvre Museum.",
        "rating": 4.8,
    },
    {
        "id": "maui_hawaii",
        "name": "Maui, Hawaii",
        "category": "Beach & Nature",
        "country": "USA",
        "estimated_cost_per_day": 320,
        "best_season": "Year-round",
        "description": "Known for world-famous beaches, the sacred Iao Valley, views of migrating humpback whales, and the scenic Hana Highway.",
        "rating": 4.9,
    },
    {
        "id": "reykjavik_iceland",
        "name": "Reykjavik, Iceland",
        "category": "Adventure & Nature",
        "country": "Iceland",
        "estimated_cost_per_day": 220,
        "best_season": "Winter for Aurora, Summer for Midnight Sun",
        "description": "Gateway to dramatic landscapes, hot springs, volcanic craters, geothermal pools, and the breathtaking Northern Lights.",
        "rating": 4.7,
    },
    {
        "id": "rome_italy",
        "name": "Rome, Italy",
        "category": "Culture & Gastronomy",
        "country": "Italy",
        "estimated_cost_per_day": 200,
        "best_season": "Spring / Autumn",
        "description": "The Eternal City, renowned for nearly 3,000 years of globally influential art, architecture, ancient ruins, and culinary excellence.",
        "rating": 4.8,
    },
]


def seed_database():
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection("destinations")

    print(f"Seeding 'destinations' collection in project '{PROJECT_ID}'...")
    for item in SAMPLE_DESTINATIONS:
        doc_id = item["id"]
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(item)
        print(f"  ✓ Seeded destination: {item['name']} (ID: {doc_id})")

    print("Successfully seeded Firestore database!")


if __name__ == "__main__":
    seed_database()
