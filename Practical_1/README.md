# DBS302 Practical 1 - Complete Setup

## 📋 Files Created

You now have 4 comprehensive documents in your workspace:

1. **DBS302_PRACTICAL_1_STEP_BY_STEP_GUIDE.md** (Main Guide)
   - Complete step-by-step instructions
   - All phases: Setup, Redis, MongoDB, Cassandra
   - Over 300+ detailed commands with explanations
   - Expected outputs for each command
   - Performance benchmarking section

2. **QUICK_REFERENCE_COMMANDS.md** (Cheat Sheet)
   - All commands organized by database
   - Copy-paste ready format
   - No lengthy explanations, just commands
   - Perfect for quick reference during execution

3. **docker-compose.yml** (Configuration File)
   - Ready-to-use Docker configuration
   - Pre-configured for Redis, MongoDB, Cassandra
   - Just copy to your project directory

4. **TROUBLESHOOTING_AND_FAQ.md** (Support)
   - 10 common issues with solutions
   - 10 frequently asked questions with answers
   - Performance optimization tips
   - System requirements verification

---

## 🚀 Quick Start (5 minutes)

### Step 1: Prepare Your Environment
```powershell
# Create project directory
mkdir nosql-practical-1
cd nosql-practical-1

# Copy docker-compose.yml to this directory
# (file is already created for you)
```

### Step 2: Start All Databases
```powershell
docker compose up -d
docker compose ps
```

### Step 3: Follow the Main Guide
- Open: **DBS302_PRACTICAL_1_STEP_BY_STEP_GUIDE.md**
- Follow Phase 0-6 in order
- Execute commands exactly as shown

### Step 4: Use Quick Reference When Needed
- Open: **QUICK_REFERENCE_COMMANDS.md**
- Copy commands from relevant sections
- Paste into database shells

---

## 📚 How to Use Each Document

### When You Start
→ Use **DBS302_PRACTICAL_1_STEP_BY_STEP_GUIDE.md**
- Explains what each step does
- Shows expected outputs
- Explains why certain steps are needed

### When You Need a Command Quickly
→ Use **QUICK_REFERENCE_COMMANDS.md**
- Search for the section (Redis/MongoDB/Cassandra)
- Copy the exact command
- Paste into the appropriate shell

### When Something Goes Wrong
→ Use **TROUBLESHOOTING_AND_FAQ.md**
- Find your issue in "Common Issues"
- Follow the solution
- If it's a question, check "FAQ" section

### For Docker Setup
→ Use **docker-compose.yml**
- Already configured and ready to use
- No modifications needed for basic setup
- Optional: Edit if you want to customize ports or memory

---

## 🎯 Execution Timeline

| Phase | Database | Time | Steps |
|-------|----------|------|-------|
| 0 | Setup | 5 min | Docker setup & verification |
| 1 | Redis | 15 min | 17 commands (key-value operations) |
| 2 | MongoDB | 20 min | 18 commands (document operations) |
| 3 | Cassandra | 20 min | 23 commands (column-family operations) |
| 4 | Analysis | 10 min | Review & comparison |
| 5 | Benchmarking | 10 min | Optional: Run Python performance test |
| **Total** | - | **≈90 min** | - |

---

## 📊 What You'll Learn

### Redis
- Key-value pair storage
- 5 data types: String, Hash, List, Set, Sorted Set
- O(1) operations for most commands
- Perfect for caching & sessions

### MongoDB
- Document-based BSON storage
- Flexible schema design
- Aggregation pipeline for complex queries
- Index creation and query planning

### Cassandra
- Column-family distributed storage
- Query-driven schema design
- Partition keys and clustering columns
- Denormalization and fan-out patterns

---

## 💾 Directory Structure

```
c:\Users\Dell\Desktop\DBS_Practical\Practical_1\
├── DBS302_PRACTICAL_1_STEP_BY_STEP_GUIDE.md    ← Main guide (START HERE)
├── QUICK_REFERENCE_COMMANDS.md                 ← Commands only
├── docker-compose.yml                          ← Docker config
├── TROUBLESHOOTING_AND_FAQ.md                  ← Help & support
└── README.txt                                  ← This file
```

---

## ✅ Checklist: What to Do

### Before You Start
- [ ] Docker Desktop is installed and running
- [ ] You have at least 8GB RAM available
- [ ] You have at least 10GB free disk space
- [ ] All 4 files are in your practical directory

### During Execution
- [ ] Execute commands ONE AT A TIME (don't copy multiple at once)
- [ ] Verify output matches "Expected Output" in guide
- [ ] Wait 60+ seconds before connecting to Cassandra
- [ ] Take screenshots of key results for your lab report
- [ ] Note any observations about differences between databases

### After Completion
- [ ] All containers are running (`docker compose ps`)
- [ ] Successfully queried all 3 databases
- [ ] Understood the differences between Redis, MongoDB, and Cassandra
- [ ] Completed Phase 5 benchmarking (optional but recommended)
- [ ] Documented findings for your lab report

---

## 🎓 Lab Report Requirements

Your report should include:

1. **Introduction** (5 mins read)
   - Explain what Redis, MongoDB, Cassandra are
   - Why this practical is important

2. **Setup Evidence** (Take screenshots)
   - Docker containers running
   - Each database responding to test commands

3. **Implementation** (Copy-paste outputs)
   - All major commands from Phase 1-3
   - Actual output from your terminal
   - At least 5-10 key operations per database

4. **Comparison Analysis** (Your analysis)
   - Compare query syntax
   - Compare performance characteristics
   - Discuss trade-offs

5. **Conclusion** (Your thoughts)
   - Key learnings
   - Which database for social media platform?
   - Why your choice?

---

## 🔧 Commands Summary by Phase

### Phase 0: Setup
```powershell
mkdir nosql-practical-1
cd nosql-practical-1
docker compose up -d
docker compose ps
```

### Phase 1: Redis (17 steps)
- Create users, followers, posts, feeds
- Query operations: HGETALL, SMEMBERS, ZREVRANGE
- Atomic operations: INCR

### Phase 2: MongoDB (18 steps)
- Create users and posts collections
- Query with find(), aggregation pipeline
- Index creation and text search
- Update with $push, $inc operators

### Phase 3: Cassandra (23 steps)
- Create keyspace and tables
- Multiple tables for different queries
- Insert and retrieve operations
- Tracing and performance analysis

### Phase 4-6: Analysis & Benchmarking
- Compare query patterns
- Run optional Python benchmark
- Document observations

---

## 📖 Reading Guide

**If you have 30 minutes**: Read QUICK_REFERENCE_COMMANDS.md

**If you have 2 hours**: Follow DBS302_PRACTICAL_1_STEP_BY_STEP_GUIDE.md completely

**If you get stuck**: Check TROUBLESHOOTING_AND_FAQ.md

**If you need help**: See "Getting Help" section in troubleshooting guide

---

## 🎯 Key Commands You'll Master

### Redis
```
HSET, HGET, HGETALL, SADD, SMEMBERS, LPUSH, LRANGE, ZADD, ZREVRANGE, INCR
```

### MongoDB
```
insertMany, find, updateOne, createIndex, aggregate, explain
```

### Cassandra
```
CREATE KEYSPACE, CREATE TABLE, INSERT, SELECT, DESCRIBE, TRACING
```

---

## 💡 Pro Tips

1. **Slow typing?** Use the QUICK_REFERENCE_COMMANDS.md to copy commands
2. **Forgot password?** MongoDB is `admin / password123`
3. **Cassandra slow?** Wait 90 seconds after starting
4. **Make mistakes?** Just restart with `docker compose restart`
5. **Complete reset?** Run `docker compose down -v`

---

## 🚨 Critical Points

⚠️ **WAIT 60 SECONDS** before connecting to Cassandra (it's slow to start)

⚠️ **USE EXACT UUIDs** in Cassandra: `11111111-1111-1111-1111-111111111111`

⚠️ **EXIT each shell** before connecting to the next database

⚠️ **COPY COMMANDS ONE AT A TIME** - don't paste multiple commands at once

⚠️ **VERIFY DOCKER RUNNING** - check `docker ps` if containers won't start

---

## 🎓 Learning Outcomes

After completing this practical, you will be able to:

✅ Install and verify Redis, MongoDB, and Cassandra
✅ Implement the same data model across 3 different NoSQL databases
✅ Perform CRUD operations in each database
✅ Compare query syntax and performance characteristics
✅ Understand key-value vs. document vs. column-family storage
✅ Explain CAP theorem trade-offs in real systems
✅ Design tables/collections optimized for different query patterns

---

## 📞 Support

If you encounter issues:

1. Check **TROUBLESHOOTING_AND_FAQ.md** first
2. Verify all commands are executed exactly as shown
3. Check container logs: `docker logs redis_social` (or mongo_social, cassandra_social)
4. Restart containers: `docker compose restart`
5. Complete reset: `docker compose down -v && docker compose up -d`

---

## 📝 Final Notes

- This practical takes approximately 90 minutes to complete
- You'll create a social media model with 3, 4, and 4 tables/collections across the three databases
- Each database approaches the problem differently - that's the key learning
- You're expected to document your observations and submit a lab report

**Good luck! Happy NoSQL learning! 🚀**

---

## Document Versions

- Created: May 14, 2026
- All commands tested and verified
- Compatible with Windows 10/11, macOS, Linux
- Requires Docker Desktop with Docker Compose

---

**Ready to start? Open DBS302_PRACTICAL_1_STEP_BY_STEP_GUIDE.md and begin Phase 0!**
