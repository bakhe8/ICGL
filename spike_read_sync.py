import sys
from qdrant_client import QdrantClient

def verify_data_sync():
    db_path = "./data/qdrant_spike"
    print(f"🔍 Verifying Data (Sync) in {db_path}...")
    
    client = QdrantClient(path=db_path)
    
    # We need to know the collection name used in adapter
    collection_name = "icgl_memory"
    
    # Mock embedding for search (or just scroll to see if data exists)
    # Scrolling is safer than searching with random vector if we check content
    print("   Scrolling collection...")
    
    # Using scroll instead of search to avoid needing embedding
    res = client.scroll(
        collection_name=collection_name,
        limit=10,
        with_payload=True,
        with_vectors=False
    )
    
    points, _ = res
    found = False
    for point in points:
        content = point.payload.get("content", "")
        print(f"   Found Point: {content[:50]}...")
        if "Architect" in content:
            found = True
            
    if found:
        print("\n✅ SPIKE SUCCESS: Data Persisted (Verified Sync).")
        with open("spike_result.txt", "w") as f:
            f.write("SUCCESS")
    else:
        print("\n❌ SPIKE FAILED: Document not found.")
        with open("spike_result.txt", "w") as f:
            f.write("FAILURE")

if __name__ == "__main__":
    verify_data_sync()
