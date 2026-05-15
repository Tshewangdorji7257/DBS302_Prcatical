# Practical 1: Setting Up Redis, MongoDB, and Cassandra  
## Implementing a Social Media Data Model and Contrasting Query Patterns

# 1. Aim
To set up three distinct NoSQL databases — **Redis**, **MongoDB**, and **Cassandra** — on a local development environment, implement a simple social media data model in each database, and contrast their respective query patterns and performance characteristics.

# 2. Objectives

By the end of this practical, students will be able to:

- Install and verify working installations of **Redis**, **MongoDB**, and **Cassandra** on their local machines or via **Docker**.
- Understand how each database represents data differently:
  - **Redis** → Key-value pairs
  - **MongoDB** → BSON documents
  - **Cassandra** → Column-family tables
- Design and implement a **social media data model** (users, posts, and followers) suited to each database's paradigm.
- Perform **basic CRUD operations** in each database using their respective interfaces:
  - `redis-cli`
  - `mongosh`
  - `cqlsh`
- Contrast the **query syntax, flexibility, and performance characteristics** of each database.


# 3. Background Theory

## 3.1 Why Three Different NoSQL Databases?

NoSQL databases are not a single technology but a **family of systems designed to solve different data management problems**.  
The three databases covered in this practical each represent a distinct NoSQL category:

| Database | NoSQL Category | Primary Strength | CAP Positioning |
|--------|---------------|----------------|----------------|
| Redis | Key-Value Store | In-memory speed, caching, session storage | CP (configurable) |
| MongoDB | Document Store | Flexible schema, rich queries | CP (configurable) |
| Cassandra | Column-Family Store | Write-heavy workloads, linear scalability | AP (tunable) |


## 3.2 The Social Media Data Model

A **social media platform** is an ideal use case for studying NoSQL databases because it involves:

- **User profiles** — structured entities with fixed and flexible attributes.
- **Posts / Tweets / Updates** — high-volume, write-heavy data.
- **Follower relationships** — graph-like relationships.
- **Feeds and timelines** — read-heavy, time-ordered access patterns.

The same conceptual model will be implemented in **all three databases**, making it straightforward to contrast how each system approaches identical requirements.


## 3.3 CAP Theorem Recap

The **CAP theorem** states that a distributed system can guarantee only **two of the three following properties simultaneously**:

- **Consistency (C):** Every read receives the most recent write.
- **Availability (A):** Every request receives a response (not necessarily the latest data).
- **Partition Tolerance (P):** The system continues to operate despite network partitions.

Understanding this theorem is essential for **selecting the right database for a given use case**.


# 4. Tools and Requirements

## 4.1 Software Requirements

| Tool | Version (Recommended) | Purpose |
|-----|----------------------|--------|
| Docker Desktop | Latest | Container-based database setup |
| Redis | 7.x or later | Key-value store |
| MongoDB | 7.x or later | Document store |
| Apache Cassandra | 4.1.x or later | Column-family store |
| redis-cli | Bundled with Redis | Redis command-line interface |
| mongosh | 2.x or later | MongoDB shell |
| cqlsh | Bundled with Cassandra | Cassandra Query Language shell |
| Python | 3.10+ (Optional) | Performance benchmarking scripts |

---

## 4.2 Hardware Requirements

- **RAM:** Minimum **8 GB** (16 GB recommended when running all three containers simultaneously)
- **Disk:** Minimum **10 GB free space**
- **Operating System:**  
  - Windows 10/11  
  - macOS 12+  
  - Ubuntu 20.04+

---

## PHASE 0: PREREQUISITES & SETUP

### Step 0.1: Verify Docker Installation

Run this command to check if Docker is installed:

```powershell
docker --version
docker compose version
```

---

### Step 0.2: Create Project Directory

```powershell
mkdir PRACTICAL_1
cd PRACTICAL_1
```

---

### Step 0.3: Create docker-compose.yml File

Created a file named `docker-compose.yml` with the following content:

```yaml
version: "3.9"

services:
  redis:
    image: redis:7.2
    container_name: redis_social
    ports:
      - "6379:6379"
    command: redis-server --save 60 1 --loglevel warning
    volumes:
      - redis_data:/data

  mongodb:
    image: mongo:7.0
    container_name: mongo_social
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password123
    volumes:
      - mongo_data:/data/db

  cassandra:
    image: cassandra:4.1
    container_name: cassandra_social
    ports:
      - "9042:9042"
    environment:
      - CASSANDRA_CLUSTER_NAME=SocialCluster
      - CASSANDRA_DC=datacenter1
      - HEAP_NEWSIZE=128M
      - MAX_HEAP_SIZE=512M
    volumes:
      - cassandra_data:/var/lib/cassandra

volumes:
  redis_data:
  mongo_data:
  cassandra_data:
```

---

### Step 0.4: Start All Containers

```powershell
docker compose up -d
```
![alt text](image.png)

**This command will**:
- Download the container images 
- Start Redis, MongoDB, and Cassandra in the background

---

### Step 0.5: Verify All Containers Are Running

```powershell
docker compose ps
```
![alt text](image-1.png)


---

---

## PHASE 1: REDIS - KEY-VALUE SOCIAL MEDIA MODEL

### Step 1.1: Connect to Redis

```powershell
docker exec -it redis_social redis-cli
```

---

### Step 1.2: Verify Redis Connection

```redis
PING
```
![alt text](image-2.png)


---

### Step 1.3: Create User Profiles Using Hashes

Each user is stored as a Hash under key `user:{user_id}`.

```redis
HSET user:1001 username "alice" name "Alice Johnson" bio "Software engineer and coffee lover." joined "2024-01-15" followers_count 0 following_count 0
```

```redis
HSET user:1002 username "bob" name "Bob Smith" bio "Tech enthusiast and open-source contributor." joined "2024-02-20" followers_count 0 following_count 0
```

```redis
HSET user:1003 username "carol" name "Carol Williams" bio "Designer and digital artist." joined "2024-03-10" followers_count 0 following_count 0
```
![alt text](image-3.png)

---

### Step 1.4: Retrieve Full User Profile

```redis
HGETALL user:1001
```
![alt text](image-4.png)

---

### Step 1.5: Retrieve Specific Field

```redis
HGET user:1001 username
```

![alt text](image-5.png)


---

### Step 1.6: Model Follower Relationships Using Sets

Alice (1001) follows Bob (1002) and Carol (1003):

```redis
SADD following:1001 1002 1003
```

Bob and Carol become followers of Alice:

```redis
SADD followers:1002 1001
SADD followers:1003 1001
```

Bob (1002) follows Carol (1003):

```redis
SADD following:1002 1003
```

Carol becomes follower of Bob:

```redis
SADD followers:1003 1002
```

![alt text](image-6.png)

---

### Step 1.7: Retrieve All Users That Alice Follows

```redis
SMEMBERS following:1001
```
![alt text](image-7.png)

---

### Step 1.8: Check If Alice Follows Bob

```redis
SISMEMBER following:1001 1002
```

![alt text](image-8.png)


---

### Step 1.9: Find Mutual Followers Between Alice and Bob

```redis
SINTERSTORE mutual:1001:1002 following:1001 following:1002
```

```redis
SMEMBERS mutual:1001:1002
```

![alt text](image-9.png)

---

### Step 1.10: Update Follower Counts in User Hashes

```redis
HINCRBY user:1001 following_count 2
```

```redis
HINCRBY user:1002 followers_count 1
```

```redis
HINCRBY user:1003 followers_count 2
```

![alt text](image-10.png)

---

### Step 1.11: Create Posts Using Hashes

Each post is stored as a Hash with a unique post ID:

```redis
HSET post:p001 user_id 1001 content "Just set up my NoSQL development environment. Redis is incredibly fast!" timestamp "2025-05-01T10:00:00Z" likes 0
```

```redis
HSET post:p002 user_id 1001 content "MongoDB's document model makes data modeling so intuitive." timestamp "2025-05-01T11:30:00Z" likes 0
```

```redis
HSET post:p003 user_id 1002 content "Learning about CAP theorem today. Fascinating trade-offs in distributed systems." timestamp "2025-05-01T09:00:00Z" likes 0
```

![alt text](image-11.png)

---

### Step 1.12: Create User Timelines Using Lists

```redis
LPUSH timeline:1001 p001 p002
```

```redis
LPUSH timeline:1002 p003
```

![alt text](image-12.png)

---

### Step 1.13: Retrieve Alice's 10 Most Recent Posts

```redis
LRANGE timeline:1001 0 9
```

![alt text](image-13.png)

---

### Step 1.14: Create News Feed Using Sorted Sets

A Sorted Set stores post IDs with Unix timestamps as scores:

```redis
ZADD feed:1003 1746345600 p001
```

```redis
ZADD feed:1003 1746352200 p002
```

```redis
ZADD feed:1003 1746338400 p003
```

![alt text](image-14.png)

---

### Step 1.15: Retrieve Carol's Feed (Most Recent First)

```redis
ZREVRANGE feed:1003 0 9 WITHSCORES
```

![alt text](image-15.png)

---

### Step 1.16: Implement Like Counter Using Atomic Increment

```redis
INCR post:p001:likes
```

```redis
INCR post:p001:likes
```

```redis
INCR post:p001:likes
```

```redis
GET post:p001:likes
```

![alt text](image-16.png)

---

### Step 1.17: Exit Redis

```redis
EXIT
```

---

---

## PHASE 2: MONGODB - DOCUMENT SOCIAL MEDIA MODEL

### Step 2.1: Connect to MongoDB

```powershell
docker exec -it mongo_social mongosh -u admin -p password123 --authenticationDatabase admin
```

---

### Step 2.2: Switch to Social Media Database

```mongosh
use social_media_db
```

![alt text](image-17.png)

---

### Step 2.3: Create Users Collection

```mongosh
db.users.insertMany([
  {
    _id: "user_1001",
    username: "alice",
    name: "Alice Johnson",
    bio: "Software engineer and coffee lover.",
    joined: new Date("2024-01-15"),
    followers_count: 2,
    following_count: 1,
    following: ["user_1002", "user_1003"]
  },
  {
    _id: "user_1002",
    username: "bob",
    name: "Bob Smith",
    bio: "Tech enthusiast and open-source contributor.",
    joined: new Date("2024-02-20"),
    followers_count: 1,
    following_count: 1,
    following: ["user_1003"]
  },
  {
    _id: "user_1003",
    username: "carol",
    name: "Carol Williams",
    bio: "Designer and digital artist.",
    joined: new Date("2024-03-10"),
    followers_count: 2,
    following_count: 0,
    following: []
  }
])
```

![alt text](image-18.png)

---

### Step 2.4: Create Posts Collection

```mongosh
db.posts.insertMany([
  {
    _id: "post_p001",
    user_id: "user_1001",
    username: "alice",
    content: "Just set up my NoSQL development environment. Redis is incredibly fast!",
    created_at: new Date("2025-05-01T10:00:00Z"),
    likes: [],
    comments: [],
    tags: ["redis", "nosql", "databases"]
  },
  {
    _id: "post_p002",
    user_id: "user_1001",
    username: "alice",
    content: "MongoDB's document model makes data modeling so intuitive.",
    created_at: new Date("2025-05-01T11:30:00Z"),
    likes: ["user_1002"],
    comments: [
      {
        user_id: "user_1002",
        username: "bob",
        text: "Absolutely agree! Especially for nested data.",
        created_at: new Date("2025-05-01T12:00:00Z")
      }
    ],
    tags: ["mongodb", "nosql", "datamodeling"]
  },
  {
    _id: "post_p003",
    user_id: "user_1002",
    username: "bob",
    content: "Learning about CAP theorem today. Fascinating trade-offs in distributed systems.",
    created_at: new Date("2025-05-01T09:00:00Z"),
    likes: ["user_1001", "user_1003"],
    comments: [],
    tags: ["cap", "distributed-systems", "nosql"]
  },
  {
    _id: "post_p004",
    user_id: "user_1003",
    username: "carol",
    content: "Designed a new UI mockup for a social feed. Sharing soon!",
    created_at: new Date("2025-05-01T14:00:00Z"),
    likes: [],
    comments: [],
    tags: ["design", "ui", "ux"]
  }
])
```

![alt text](image-19.png)

---

### Step 2.5: Basic Read Queries - Retrieve All Posts by Alice

```mongosh
db.posts.find({ user_id: "user_1001" }).pretty()
```

![alt text](image-20.png)

---

### Step 2.6: Retrieve Only Content and Creation Date (Projection)

```mongosh
db.posts.find(
  { user_id: "user_1001" },
  { content: 1, created_at: 1, _id: 0 }
)
```

![alt text](image-21.png)

---

### Step 2.7: Find Posts Containing Tag "nosql"

```mongosh
db.posts.find({ tags: "nosql" }).pretty()
```

![alt text](image-22.png)

---

### Step 2.8: Find Posts With At Least One Like

```mongosh
db.posts.find({ "likes.0": { $exists: true } })
```

![alt text](image-23.png)

Posts that have at least one like (p002 and p003)

---

### Step 2.9: Add a Like to a Post

```mongosh
db.posts.updateOne(
  { _id: "post_p001" },
  {
    $push: { likes: "user_1003" }
  }
)
```

![alt text](image-24.png)

---

### Step 2.10: Add a Comment to a Post

```mongosh
db.posts.updateOne(
  { _id: "post_p001" },
  {
    $push: {
      comments: {
        user_id: "user_1003",
        username: "carol",
        text: "Great setup! Which OS are you using?",
        created_at: new Date()
      }
    }
  }
)
```

![alt text](image-25.png)

---

### Step 2.11: Verify the Update - Retrieve Updated Post

```mongosh
db.posts.findOne({ _id: "post_p001" }).pretty()
```

Post p001 should now have 1 like (user_1003) and 1 comment

---

### Step 2.12: Aggregation Framework - Build Social Feed

This advanced query builds a feed of posts from users that Alice follows:

```mongosh
db.posts.aggregate([
  // Stage 1: Filter posts from users that Alice follows
  {
    $match: {
      user_id: { $in: ["user_1002", "user_1003"] }
    }
  },
  // Stage 2: Sort by creation time, most recent first
  {
    $sort: { created_at: -1 }
  },
  // Stage 3: Limit to the 10 most recent posts
  {
    $limit: 10
  },
  // Stage 4: Project only the fields needed for the feed
  {
    $project: {
      username: 1,
      content: 1,
      created_at: 1,
      likes_count: { $size: { $ifNull: ["$likes", []] } },
      comments_count: { $size: { $ifNull: ["$comments", []] } }
    }
  }
])
```

![alt text](image-26.png)
 
Posts from Bob and Carol with like and comment counts

---

### Step 2.13: Create Index on user_id

```mongosh
db.posts.createIndex({ user_id: 1 })
```

![alt text](image-27.png)

---

### Step 2.14: Create Compound Index for Feed Queries

```mongosh
db.posts.createIndex({ user_id: 1, created_at: -1 })
```

![alt text](image-28.png)

---

### Step 2.15: Create Text Index for Full-Text Search

```mongosh
db.posts.createIndex({ content: "text", tags: "text" })
```

![alt text](image-29.png)

---

### Step 2.16: Use Text Index for Search

```mongosh
db.posts.find({ $text: { $search: "distributed systems" } })
```
![alt text](image-30.png)

Posts containing "distributed systems

---

### Step 2.17: Verify Indexes

```mongosh
db.posts.getIndexes()
```
![alt text](image-31.png)

Array of all indexes on the posts collection

---

### Step 2.18: Explain Query Execution Plan

This shows whether the query uses an index or does a full collection scan:

```mongosh
db.posts.find({ user_id: "user_1001" }).explain("executionStats")
```

![alt text](image-32.png)
![alt text](image-33.png)

**Look for**: `stage: "COLLSCAN"` (bad, no index used) or `stage: "IXSCAN"` (good, index used)

---

### Step 2.19: Exit MongoDB

```mongosh
exit
```
---

---

## PHASE 3: CASSANDRA - COLUMN-FAMILY SOCIAL MEDIA MODEL

###  WAIT BEFORE PROCEEDINGm

```powershell
Start-Sleep -Seconds 60
```

---

### Step 3.1: Connect to Cassandra

```powershell
docker exec -it cassandra_social cqlsh
```

![alt text](image-34.png)

---

### Step 3.2: Verify Cassandra Connection

```cassandra
DESCRIBE CLUSTER;
```

![alt text](image-35.png) 

Cluster information (Cluster Name: SocialCluster)

---

### Step 3.3: Create Keyspace

A keyspace is like a database in Cassandra:

```cassandra
CREATE KEYSPACE IF NOT EXISTS social_media
WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};
```

![alt text](image-36.png)

---

### Step 3.4: Use the Keyspace

```cassandra
USE social_media;
```

![alt text](image-37.png)

---

### Step 3.5: Create Users Table

```cassandra
CREATE TABLE IF NOT EXISTS users (
    user_id     UUID,
    username    TEXT,
    name        TEXT,
    bio         TEXT,
    joined      TIMESTAMP,
    PRIMARY KEY (user_id)
);
```

![alt text](image-38.png)

---

### Step 3.6: Insert User Records

```cassandra
INSERT INTO users (user_id, username, name, bio, joined)
VALUES (11111111-1111-1111-1111-111111111111, 'alice', 'Alice Johnson', 'Software engineer and coffee lover.', '2024-01-15 00:00:00+0000');
```

```cassandra
INSERT INTO users (user_id, username, name, bio, joined)
VALUES (22222222-2222-2222-2222-222222222222, 'bob', 'Bob Smith', 'Tech enthusiast and open-source contributor.', '2024-02-20 00:00:00+0000');
```

```cassandra
INSERT INTO users (user_id, username, name, bio, joined)
VALUES (33333333-3333-3333-3333-333333333333, 'carol', 'Carol Williams', 'Designer and digital artist.', '2024-03-10 00:00:00+0000');
```

![alt text](image-39.png)

---

### Step 3.7: Create Posts by User Table

This table is optimized for: "Give me all posts by user X, ordered by time"

```cassandra
CREATE TABLE IF NOT EXISTS posts_by_user (
    user_id     UUID,
    created_at  TIMESTAMP,
    post_id     UUID,
    username    TEXT,
    content     TEXT,
    tags        SET<TEXT>,
    likes_count INT,
    PRIMARY KEY (user_id, created_at, post_id)
) WITH CLUSTERING ORDER BY (created_at DESC, post_id ASC);
```

![alt text](image-40.png)

---

### Step 3.8: Insert Posts - Alice's First Post

```cassandra
INSERT INTO posts_by_user (user_id, created_at, post_id, username, content, tags, likes_count)
VALUES (
    11111111-1111-1111-1111-111111111111,
    '2025-05-01 10:00:00+0000',
    uuid(),
    'alice',
    'Just set up my NoSQL development environment. Redis is incredibly fast!',
    {'redis', 'nosql', 'databases'},
    0
);
```

![alt text](image-41.png)

---

### Step 3.9: Insert Posts - Alice's Second Post

```cassandra
INSERT INTO posts_by_user (user_id, created_at, post_id, username, content, tags, likes_count)
VALUES (
    11111111-1111-1111-1111-111111111111,
    '2025-05-01 11:30:00+0000',
    uuid(),
    'alice',
    'MongoDB''s document model makes data modeling so intuitive.',
    {'mongodb', 'nosql', 'datamodeling'},
    1
);
```

![alt text](image-42.png)

---

### Step 3.10: Insert Posts - Bob's Post

```cassandra
INSERT INTO posts_by_user (user_id, created_at, post_id, username, content, tags, likes_count)
VALUES (
    22222222-2222-2222-2222-222222222222,
    '2025-05-01 09:00:00+0000',
    uuid(),
    'bob',
    'Learning about CAP theorem today. Fascinating trade-offs in distributed systems.',
    {'cap', 'distributed-systems', 'nosql'},
    2
);
```

![alt text](image-43.png)

---

### Step 3.11: Retrieve All Posts by Alice

```cassandra
SELECT username, content, created_at, likes_count
FROM posts_by_user
WHERE user_id = 11111111-1111-1111-1111-111111111111;
```

![alt text](image-44.png)

Alice's 2 posts in chronological order (most recent first)

---

### Step 3.12: Create Followers Table

This table answers: "Who follows user X?"

```cassandra
CREATE TABLE IF NOT EXISTS followers (
    user_id         UUID,
    follower_id     UUID,
    follower_username TEXT,
    followed_at     TIMESTAMP,
    PRIMARY KEY (user_id, follower_id)
);
```

![alt text](image-45.png)

---

### Step 3.13: Insert Follower Relationships

Bob follows Alice:

```cassandra
INSERT INTO followers (user_id, follower_id, follower_username, followed_at)
VALUES (11111111-1111-1111-1111-111111111111, 22222222-2222-2222-2222-222222222222, 'bob', toTimestamp(now()));
```

Carol follows Alice:

```cassandra
INSERT INTO followers (user_id, follower_id, follower_username, followed_at)
VALUES (11111111-1111-1111-1111-111111111111, 33333333-3333-3333-3333-333333333333, 'carol', toTimestamp(now()));
```

![alt text](image-46.png)

---

### Step 3.14: Retrieve All Followers of Alice

```cassandra
SELECT follower_username, followed_at
FROM followers
WHERE user_id = 11111111-1111-1111-1111-111111111111;
```

![alt text](image-47.png)

Bob and Carol as followers of Alice

---

### Step 3.15: Create Timeline/News Feed Table

This is a denormalized table where posts are duplicated to followers' feeds (fan-out-on-write pattern):

```cassandra
CREATE TABLE IF NOT EXISTS timeline_by_user (
    user_id     UUID,
    created_at  TIMESTAMP,
    post_id     UUID,
    author_id   UUID,
    author_name TEXT,
    content     TEXT,
    likes_count INT,
    PRIMARY KEY (user_id, created_at, post_id)
) WITH CLUSTERING ORDER BY (created_at DESC, post_id ASC);
```

![alt text](image-48.png)

---

### Step 3.16: Insert Alice's Post Into Bob's Timeline

```cassandra
INSERT INTO timeline_by_user (user_id, created_at, post_id, author_id, author_name, content, likes_count)
VALUES (
    22222222-2222-2222-2222-222222222222,
    '2025-05-01 10:00:00+0000',
    uuid(),
    11111111-1111-1111-1111-111111111111,
    'alice',
    'Just set up my NoSQL development environment. Redis is incredibly fast!',
    0
);
```

![alt text](image-49.png)

---

### Step 3.17: Insert Alice's Post Into Carol's Timeline

```cassandra
INSERT INTO timeline_by_user (user_id, created_at, post_id, author_id, author_name, content, likes_count)
VALUES (
    33333333-3333-3333-3333-333333333333,
    '2025-05-01 10:00:00+0000',
    uuid(),
    11111111-1111-1111-1111-111111111111,
    'alice',
    'Just set up my NoSQL development environment. Redis is incredibly fast!',
    0
);
```

![alt text](image-50.png)

---

### Step 3.18: Retrieve Bob's News Feed

```cassandra
SELECT author_name, content, created_at, likes_count
FROM timeline_by_user
WHERE user_id = 22222222-2222-2222-2222-222222222222
LIMIT 20;
```

![alt text](image-51.png) 

Alice's posts that Bob can see in his timeline

---

### Step 3.19: Enable Tracing for Performance Analysis

```cassandra
TRACING ON;
```

![alt text](image-52.png)

---

### Step 3.20: Run Query With Tracing

```cassandra
SELECT author_name, content, created_at
FROM timeline_by_user
WHERE user_id = 22222222-2222-2222-2222-222222222222
LIMIT 10;
```

![alt text](image-53.png) 

Query results followed by detailed tracing information showing execution time at each step

---

### Step 3.21: Disable Tracing

```cassandra
TRACING OFF;
```

![alt text](image-54.png)

---

### Step 3.22: Demonstrate Query Limitation - Why Schema Design Matters

Try to query posts by username (this will fail or show why it's problematic):

```cassandra
-- This query will fail - Cassandra can only query on partition and clustering keys
SELECT * FROM posts_by_user WHERE username = 'alice' ALLOW FILTERING;
```

![alt text](image-55.png)

**Important**: This demonstrates why Cassandra requires to design tables around specific queries. It cannot use `ALLOW FILTERING` in production - it's too slow.

---

### Step 3.23: Exit Cassandra

```cassandra
exit
```

---

## PHASE 4: PERFORMANCE BENCHMARKING 

To measure performance across all three databases.

### Step 5.1: Install Python Dependencies

```powershell
pip install redis pymongo cassandra-driver
```

---

### Step 5.2: Create benchmark.py File

Create a file named `benchmark.py`.

```python
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
```

---

### Step 5.3: Run the Benchmark

```powershell
cd nosql-practical-1
python benchmark.py
```

![alt text](image-56.png)

---

## Comparison Analysis

### 1. Data Modeling Philosophy

| Aspect | Redis | MongoDB | Cassandra |
|--------|-------|---------|-----------|
| **Data Organization** | Flat key-value pairs | Nested BSON documents | Partitioned rows with clustering |
| **Schema Enforcement** | None (key-value pairs) | Optional (can use validators) | Strict (DDL required) |
| **Relationship Modeling** | Manual via separate keys | Embedding or referencing | Denormalization (duplication) |
| **Query Design** | Application-driven | Entity-driven | Query-driven (model-first) |
| **Flexibility** | Very flexible, no schema | Very flexible schema | Rigid, predetermined queries |

**Analysis**: 
- Redis requires developers to manually manage relationships through separate keys
- MongoDB allows flexible embedding, reducing joins
- Cassandra requires pre-planning of queries, enforcing explicit schema design

---

### 2. Query Pattern Comparison

**Problem**: "Retrieve the 10 most recent posts from user Alice"

#### Redis Approach (2-3 Round Trips):
```redis
LRANGE timeline:alice 0 9          -- Get post IDs
HGETALL post:p001                  -- Get each post's content (multiple commands)
```
- **Time Complexity**: O(N+M) where N=operations, M=posts
- **Network Overhead**: High (multiple round trips)
- **Advantage**: Simple, in-memory speed

#### MongoDB Approach (1 Round Trip):
```mongodb
db.posts.find({ user_id: "user_1001" })
  .sort({ created_at: -1 })
  .limit(10)
```
- **Time Complexity**: O(log N) with index
- **Network Overhead**: Single query
- **Advantage**: Complete documents in one query, flexible filtering

#### Cassandra Approach (1 Round Trip):
```cassandra
SELECT * FROM posts_by_user
WHERE user_id = 11111111-1111-1111-1111-111111111111
LIMIT 10;
```
- **Time Complexity**: O(log N) for partition lookup + O(M) for clustering scan
- **Network Overhead**: Single query, data pre-sorted
- **Advantage**: Data already in optimal order at storage level

---

### 3. Query Syntax Comparison

| Operation | Redis | MongoDB | Cassandra |
|-----------|-------|---------|-----------|
| **Create** | HSET, SADD, LPUSH | insertMany | INSERT |
| **Read Single** | HGETALL | findOne | SELECT WHERE |
| **Read Multiple** | SMEMBERS, LRANGE | find with filter | SELECT WHERE LIMIT |
| **Update** | HINCRBY, HSET | updateOne, $inc, $push | UPDATE SET |
| **Delete** | DEL | deleteOne | DELETE WHERE |
| **Complex Query** | Manual in app | aggregation pipeline | Requires separate table |
| **Index** | Automatic | createIndex | Part of schema |

**Analysis**: 
- **Redis**: Simple commands, minimal abstraction
- **MongoDB**: Rich query language similar to SQL with aggregations
- **Cassandra**: SQL-like syntax but much more limited query flexibility

---

### 4. Performance Characteristics (Benchmark Results)

Based on our Python benchmark with 500 records:

| Metric | Redis | MongoDB | Cassandra |
|--------|-------|---------|-----------|
| **Write Speed** | 14,753 ops/sec | 6,228 ops/sec | Not available* |
| **Read Speed** | 41,009 ops/sec | 12,347 ops/sec | Not available* |
| **Write Ratio** | 1x (baseline) | 0.42x | - |
| **Read Ratio** | 1x (baseline) | 0.30x | - |
| **Memory Usage** | High (in-memory) | Moderate (on-disk) | Low (optimized) |
| **Persistence** | Optional (RDB/AOF) | Always (journaling) | Always (LSM tree) |
| **Latency** | Sub-ms | 1-10ms | 1-5ms |
| **Horizontal Scale** | Limited | Sharding | Linear |

*Cassandra driver unavailable in Python 3.12 environment; would perform differently at scale

**Key Findings**:
- **Redis is 2.4x faster for writes** (in-memory advantage)
- **Redis is 3.3x faster for reads** (no parsing overhead)
- **MongoDB trades speed for query flexibility**
- **Cassandra optimized for scale, not single-node performance**

---

### 5. Write vs. Read Trade-offs

| Scenario | Redis | MongoDB | Cassandra |
|----------|-------|---------|-----------|
| **Write a new post** | Very Fast | Fast | Very Fast (scales) |
| **Read single post** | 1 query | 1 query | 1 query |
| **Get user's posts** | 2+ queries | 1 query | 1 query |
| **Build news feed** | Manual fan-out | Aggregation pipeline | Pre-computed (fan-out-on-write) |
| **Ad-hoc queries** | Manual logic | Excellent | Not supported |
| **Flexible schema** | Very high | Very high | Very low |
| **Strong consistency** | Yes (single-node) | Yes (configurable) | Eventual (tunable) |

**Trade-off Analysis**:
- **Redis**: Optimized for writes/reads, requires manual query logic
- **MongoDB**: Balanced, supports complex queries, trades some performance
- **Cassandra**: Optimized for large-scale writes, rigid query model

---

### 6. Consistency & Availability

**CAP Theorem Positioning**:

| Database | Consistency | Availability | Partition Tolerance |
|----------|-------------|--------------|-------------------|
| **Redis** | Strong (single node) | Yes | Configurable* |
| **MongoDB** | Strong (default) | Yes | Tunable |
| **Cassandra** | Eventual (default) | Strong | Strong |

*Redis Cluster provides AP with configurable consistency

**Practical Implications**:
- **Redis**: Perfect for scenarios needing strong consistency with single point of failure acceptable
- **MongoDB**: Good for most applications needing strong consistency
- **Cassandra**: Ideal for scenarios that must remain available during network partitions

---

## Performance Benchmarking Results

### Benchmark Environment
- **System**: Windows 11
- **Python**: 3.12
- **Test Records**: 500 posts
- **Containers**: Docker with isolated networks

### Detailed Results

```
--- Write Benchmark (500 records) ---
  Redis   : 0.0339s  (14,753 ops/sec)  Fastest
  MongoDB : 0.0803s  (6,228 ops/sec)
  Cassandra: Skipped (driver unavailable)

--- Read Benchmark (retrieve 500 records) ---
  Redis   : 0.0122s  (41,009 ops/sec)  Fastest
  MongoDB : 0.0405s  (12,347 ops/sec)
  Cassandra: Skipped (driver unavailable)
```

### Performance Analysis

**Write Performance:**
- Redis completes 500 writes in **34ms** using pipelined operations
- MongoDB takes **80ms** due to parsing and disk I/O
- **Conclusion**: Redis is ideal for high-frequency write operations (counters, logs)

**Read Performance:**
- Redis retrieves 500 records in **12ms** from memory
- MongoDB takes **40ms** with indexed queries
- **Conclusion**: Redis caches should be used for frequently accessed data

**Scalability Implications:**
- **Redis**: At 14,753 ops/sec, can handle ~42GB/day of 1KB records (single node)
- **MongoDB**: At 6,228 ops/sec, can handle ~17GB/day with durability
- **Cassandra**: (Estimated) At scale, handles > 100GB/day across nodes

---

## Conclusion

### Key Learnings

1. **No One-Size-Fits-All Solution**
   - Each database excels in different scenarios
   - Selecting the right database is a critical architectural decision

2. **Trade-offs Are Fundamental**
   - Speed vs. Flexibility (Redis vs. MongoDB)
   - Query Flexibility vs. Scalability (MongoDB vs. Cassandra)
   - Consistency vs. Availability (Redis/MongoDB vs. Cassandra)

3. **Data Modeling Paradigms Differ Drastically**
   - Redis: Application-level relationship management
   - MongoDB: Document-oriented embedding
   - Cassandra: Query-driven denormalized schemas

4. **Performance Characteristics Vary**
   - Redis: Ultra-fast but single-machine limited
   - MongoDB: Good balance of performance and flexibility
   - Cassandra: Optimized for scale, not single-instance performance

5. **CAP Theorem Constraints Are Real**
   - Every system makes explicit trade-offs
   - Understanding these trade-offs enables better architecture

---

### Recommendation: Database Selection for Social Media Platform

#### Proposed Architecture: **Polyglot Persistence**

For a production social media platform like Instagram or Twitter, I recommend using **all three databases together** in a layered architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    User Application                      │
└──────────────────────────┬──────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│    Redis     │  │  MongoDB     │  │  Cassandra   │
│  (Cache)     │  │  (Current)   │  │  (Archive)   │
│              │  │              │  │              │
│• Sessions    │  │• User prof.  │  │• Event logs  │
│• Tokens      │  │• Posts       │  │• Analytics   │
│• Feeds       │  │• Comments    │  │• Timeseries  │
│• Counters    │  │• Follows     │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

**Detailed Justification**:

#### 1. **Redis for Real-Time Cache & Sessions** 
- **Session Storage**: User authentication tokens with automatic expiration (TTL)
- **Feed Cache**: Pre-computed news feeds cached for active users
- **Counters**: Like counts, share counts, view counts (atomic increments)
- **Leaderboards**: Trending hashtags using sorted sets
- **Rate Limiting**: API rate limits per user
- **Reasoning**: Sub-millisecond response times critical for user experience

#### 2. **MongoDB for Core Data** 
- **User Profiles**: Flexible schema for user attributes (verified, badges, etc.)
- **Posts**: Complete post documents with embedded comments
- **Ad-Hoc Queries**: Search, filtering, analytics reporting
- **Aggregations**: Complex queries like "top trending tags", "users with most followers"
- **Reasoning**: Query flexibility needed for business intelligence and recommendations

#### 3. **Cassandra for Historical Data** 
- **Event Logs**: Immutable log of all user actions for compliance
- **Analytics**: Time-series data for user behavior analysis
- **Audit Trail**: Who liked what post when (compliance requirement)
- **Archival**: Keep hot data in MongoDB, move to Cassandra after 90 days
- **Reasoning**: Designed for massive scale, handles 10+ years of data efficiently

---

### Implementation Strategy

**Write Path** (User creates post):
1. Write to **MongoDB** (authoritative source)
2. Cache in **Redis** (for quick retrieval)
3. Fan-out to followers' feed caches
4. Log event to **Cassandra** (asynchronous)

**Read Path** (User views feed):
1. Check **Redis** cache first (instant)
2. If miss, query **MongoDB** (fast)
3. Update cache for next time

**Analytics Path** (Running reports):
1. Query **Cassandra** for historical data
2. Aggregate trends
3. Store results in **MongoDB** for dashboard

---

### Why This Architecture?

| Layer | Database | Use Case | Benefit |
|-------|----------|----------|---------|
| **Hot** | Redis | Active sessions, feeds, counters | 10-100ms response time |
| **Warm** | MongoDB | User data, posts, comments | 100-500ms, flexible queries |
| **Cold** | Cassandra | Event logs, analytics, archive | 1-5 seconds, unlimited scale |

This approach provides:
- **Performance**: 10-100ms responses for 95% of queries
- **Scalability**: Can handle billions of users
- **Flexibility**: Can adapt to changing requirements
- **Compliance**: Audit trail and immutable event log
- **Cost**: Pay for what you use (cache/warm/cold tiers)

---

### Alternative Scenarios

**If Starting Small** (< 1M users):
- **Use MongoDB only** for simplicity and query flexibility
- Add Redis caching if performance becomes issue
- Cassandra not needed until 100M+ users

**If Real-Time Streaming** (Twitch-like):
- **Prioritize Cassandra** for handling massive write load
- Use Redis for active viewer caches
- MongoDB for metadata

**If Ad-Hoc Analytics** (Business Intelligence):
- **Prioritize MongoDB** for query flexibility
- Redis for common dashboards
- Cassandra only if data > 1TB

---

## Final Thoughts

This practical demonstrates that modern application architecture is about **choosing the right tool for each job**. Rather than forcing a single database to do everything, successful platforms like Netflix, Uber, and Twitter use polyglot persistence to optimize different aspects of their systems.

The key learnings are:
1. Understand your workload (reads vs. writes, consistency requirements)
2. Know your database's strengths and limitations
3. Combine multiple databases strategically
4. Monitor and optimize based on real performance data

By mastering Redis, MongoDB, and Cassandra, you're equipped to architect systems at any scale.

---

## References

- Redis Documentation: https://redis.io/documentation
- MongoDB Documentation: https://docs.mongodb.com/
- Apache Cassandra Documentation: https://cassandra.apache.org/doc/latest/
- CAP Theorem: https://en.wikipedia.org/wiki/CAP_theorem
- Designing Data-Intensive Applications (Book): Martin Kleppmann




