import os
import sys
import time
import uuid
import redis
import pymongo

# Fix for Python 3.12+ compatibility with cassandra-driver
if sys.version_info >= (3, 12):
    # For Python 3.12+, we need to use asyncio event loop manager
    os.environ['CASSANDRA_DRIVER_EVENT_LOOP_MANAGER'] = 'cassandra.io.AsyncioEventLoopManager'

# Try to import Cassandra driver - may fail on first attempt
Cluster = None
PlainTextAuthProvider = None
CASSANDRA_AVAILABLE_IMPORT = False

try:
    from cassandra.cluster import Cluster
    from cassandra.auth import PlainTextAuthProvider
    CASSANDRA_AVAILABLE_IMPORT = True
except Exception as e:
    print(f"Note: Cassandra driver not available - {type(e).__name__}: {str(e)[:100]}\n")
    CASSANDRA_AVAILABLE_IMPORT = False

# -------------------------------------------------------------------
# Connection setup
# -------------------------------------------------------------------

# Redis connection
redis_available = False
try:
    r = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_connect_timeout=5)
    r.ping()
    redis_available = True
except Exception as e:
    print(f"⚠️  Warning: Could not connect to Redis. Error: {e}")
    redis_available = False

# MongoDB connection
mongo_available = False
mongo_client = None
mongo_posts = None
try:
    # Try with authentication first
    mongo_client = pymongo.MongoClient(
        "mongodb://admin:password123@localhost:27017/",
        serverSelectionTimeoutMS=3000
    )
    mongo_db = mongo_client["benchmark_db"]
    mongo_posts = mongo_db["posts"]
    mongo_posts.drop()  # Clean up before benchmark
    mongo_available = True
except Exception as auth_err:
    # Fall back to no authentication
    try:
        mongo_client = pymongo.MongoClient(
            "mongodb://localhost:27017/",
            serverSelectionTimeoutMS=3000
        )
        mongo_db = mongo_client["benchmark_db"]
        mongo_posts = mongo_db["posts"]
        mongo_posts.drop()  # Clean up before benchmark
        mongo_available = True
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to MongoDB. Error: {e}")
        mongo_available = False

# Cassandra connection
cassandra_available = False
cass_session = None
cass_cluster = None

if CASSANDRA_AVAILABLE_IMPORT:
    try:
        cass_cluster = Cluster(['localhost'], connect_timeout=5)
        cass_session = cass_cluster.connect(wait_for_all_pools=True)

        cass_session.execute("""
            CREATE KEYSPACE IF NOT EXISTS benchmark
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
        """)
        cass_session.set_keyspace('benchmark')
        cass_session.execute("DROP TABLE IF EXISTS posts_bench")
        cass_session.execute("""
            CREATE TABLE posts_bench (
                user_id  UUID,
                post_id  UUID,
                content  TEXT,
                created_at TIMESTAMP,
                PRIMARY KEY (user_id, created_at, post_id)
            ) WITH CLUSTERING ORDER BY (created_at DESC, post_id ASC)
        """)
        cassandra_available = True
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to Cassandra. Error: {e}")
        print(f"Continuing benchmark with Redis and MongoDB only...\n")
        cassandra_available = False

# -------------------------------------------------------------------
# Benchmark parameters
# -------------------------------------------------------------------
NUM_WRITES = 500
user_id = "user_bench_001"
cass_user_id = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

# -------------------------------------------------------------------
# Write benchmark
# -------------------------------------------------------------------
print(f"\n--- Write Benchmark ({NUM_WRITES} records) ---")

# Redis writes
if redis_available:
    try:
        start = time.time()
        pipe = r.pipeline()
        for i in range(NUM_WRITES):
            post_id = f"bench_post_{i}"
            pipe.hset(f"post:{post_id}", mapping={
                "user_id": user_id,
                "content": f"Benchmark post number {i} for Redis performance testing.",
                "timestamp": "2025-05-01T10:00:00Z"
            })
            pipe.lpush(f"timeline:{user_id}", post_id)
        pipe.execute()
        redis_write_time = time.time() - start
        print(f"  Redis   : {redis_write_time:.4f}s  ({NUM_WRITES/redis_write_time:.0f} ops/sec)")
    except Exception as e:
        print(f"  Redis   : Error - {e}")
else:
    print(f"  Redis   : Skipped (not available)")

# MongoDB writes
if mongo_available:
    try:
        start = time.time()
        docs = [
            {
                "_id": f"bench_post_{i}",
                "user_id": user_id,
                "content": f"Benchmark post number {i} for MongoDB performance testing.",
                "created_at": "2025-05-01T10:00:00Z"
            }
            for i in range(NUM_WRITES)
        ]
        mongo_posts.insert_many(docs)
        mongo_write_time = time.time() - start
        print(f"  MongoDB : {mongo_write_time:.4f}s  ({NUM_WRITES/mongo_write_time:.0f} ops/sec)")
    except Exception as e:
        print(f"  MongoDB : Error - {e}")
else:
    print(f"  MongoDB : Skipped (not available)")

# Cassandra writes
if cassandra_available:
    try:
        prepared = cass_session.prepare("""
            INSERT INTO posts_bench (user_id, post_id, content, created_at)
            VALUES (?, ?, ?, toTimestamp(now()))
        """)
        start = time.time()
        for i in range(NUM_WRITES):
            cass_session.execute(prepared, (cass_user_id, uuid.uuid4(),
                                            f"Benchmark post number {i} for Cassandra performance testing."))
        cass_write_time = time.time() - start
        print(f"  Cassandra: {cass_write_time:.4f}s  ({NUM_WRITES/cass_write_time:.0f} ops/sec)")
    except Exception as e:
        print(f"  Cassandra: Error during write benchmark - {e}")
else:
    print(f"  Cassandra: Skipped (not available)")

# -------------------------------------------------------------------
# Read benchmark
# -------------------------------------------------------------------
print(f"\n--- Read Benchmark (retrieve {NUM_WRITES} records) ---")

# Redis reads
if redis_available:
    try:
        start = time.time()
        post_ids = r.lrange(f"timeline:{user_id}", 0, NUM_WRITES - 1)
        pipe = r.pipeline()
        for pid in post_ids:
            pipe.hgetall(f"post:{pid}")
        pipe.execute()
        redis_read_time = time.time() - start
        print(f"  Redis   : {redis_read_time:.4f}s  ({len(post_ids)/redis_read_time:.0f} ops/sec)")
    except Exception as e:
        print(f"  Redis   : Error - {e}")
else:
    print(f"  Redis   : Skipped (not available)")

# MongoDB reads
if mongo_available:
    try:
        mongo_posts.create_index([("user_id", pymongo.ASCENDING)])
        start = time.time()
        results = list(mongo_posts.find({"user_id": user_id}))
        mongo_read_time = time.time() - start
        print(f"  MongoDB : {mongo_read_time:.4f}s  ({len(results)/mongo_read_time:.0f} ops/sec)")
    except Exception as e:
        print(f"  MongoDB : Error - {e}")
else:
    print(f"  MongoDB : Skipped (not available)")

# Cassandra reads
if cassandra_available:
    try:
        start = time.time()
        rows = list(cass_session.execute(
            "SELECT * FROM posts_bench WHERE user_id = %s LIMIT %s",
            (cass_user_id, NUM_WRITES)
        ))
        cass_read_time = time.time() - start
        print(f"  Cassandra: {cass_read_time:.4f}s  ({len(rows)/cass_read_time:.0f} ops/sec)")
    except Exception as e:
        print(f"  Cassandra: Error during read benchmark - {e}")
else:
    print(f"  Cassandra: Skipped (not available)")

print("\n--- Benchmark Complete ---\n")

# Cleanup
if mongo_client is not None:
    try:
        mongo_client.close()
    except:
        pass

if cassandra_available and cass_cluster is not None:
    try:
        cass_cluster.shutdown()
    except:
        pass