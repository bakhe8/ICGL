import time
import asyncio
import sys
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import numpy as np

def run_benchmark(n_items=1000):
    db_path = "./data/qdrant_perf"
    print(f"\n🚀 Starting Performance Spike ({n_items} items)...")
    print(f"   Storage: {db_path}")
    
    client = QdrantClient(path=db_path)
    # Explicit delete/create
    if client.collection_exists("perf_test"):
        client.delete_collection("perf_test")
        
    client.create_collection(
        collection_name="perf_test",
        vectors_config=VectorParams(size=128, distance=Distance.COSINE),
    )
    
    # 1. Write Benchmark
    print("   Generating synthetic vectors...")
    vectors = np.random.rand(n_items, 128).tolist()
    points = [
        PointStruct(id=i, vector=v, payload={"i": i}) 
        for i, v in enumerate(vectors)
    ]
    
    print("   Starting upsert...")
    start_time = time.time()
    batch_size = 100
    for i in range(0, len(points), batch_size):
        client.upsert(
            collection_name="perf_test",
            points=points[i : i + batch_size]
        )
    duration = time.time() - start_time
    vectors_per_sec = n_items / duration if duration > 0 else 0
    print(f"   ✅ Write Latency: {duration:.4f}s ({vectors_per_sec:.0f} vectors/s)")
    
    # 2. Search Benchmark
    print("   Starting search benchmark (100 queries)...")
    query_vector = np.random.rand(128).tolist()
    
    start_time = time.time()
    for _ in range(100):
        try:
            client.search(
                collection_name="perf_test",
                query_vector=query_vector,
                limit=10
            )
        except AttributeError:
            print("   ⚠️ Client has no 'search', trying 'query_points'...")
            # Fallback for some versions?
            client.query_points(
                collection_name="perf_test",
                query=query_vector,
                limit=10
            )
            break
            
    duration = time.time() - start_time
    avg_latency = (duration / 100) * 1000
    print(f"   ✅ Search Latency: {avg_latency:.2f}ms per query")
    
    return avg_latency

if __name__ == "__main__":
    import shutil
    from pathlib import Path
    if Path("./data/qdrant_perf").exists():
        shutil.rmtree("./data/qdrant_perf")
        
    # Run 1K
    lat_1k = run_benchmark(1000)
    
    # Run 5K (Simulate reasonable load)
    # lat_5k = run_benchmark(5000) 
    
    print("\n🏁 Performance Metrics Recorded.")
    # Log to file for governance
    with open("perf_result.txt", "w") as f:
        f.write(f"1K_WRITE_MS: N/A\n")
        f.write(f"1K_SEARCH_LATENCY_MS: {lat_1k:.2f}\n")
