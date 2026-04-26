# DBS302 - Practical 3: MongoDB E-Commerce 

# AIM

To design and develop an e-commerce schema using MongoDB, build complex aggregation queries using the aggregation pipeline and indexing/query optimization techniques.

# Objective

By the completion of the above lab, we will be able to:

- Design an actual domain e-commerce scenario with users, products, sales/orders and so on in MongoDB using the document-based approach.
- Implement the above mentioned schema by creating respective collections along with required fields and data samples.
- Build aggregation pipelines with real world queries used for analytics purpose.
- Index collections using different types of indexes (i.e., single index, compound index, multi key index, text search index).
- Optimize queries with respect to performance using `explain` command.

# Expected Learning Outcomes

Following this practical exercise, we will be able to:

- Utilize "query-first" schema design: organize data based on prevailing access methods rather than strict normalization principles alone.
- Distinguish between embedding and referencing in MongoDB and explain their appropriateness for different types of relations within the domain of e-commerce.
- Create and understand complex stages in aggregation pipelines with the help of operators such as `$match`, `$group`, `$project`, `$lookup`, `$sort`, `$limit`, and accumulator functions.
- Create efficient indexes according to best practices (e.g., Equality-Sort-Range indexing order in compound indexes) and analyze queries through `explain("executionStats")`.
- Identify and prevent anti-patterns that negatively impact performance, including unconstrained document expansion and scanning collections.

## PART 1: DATABASE AND COLLECTION SETUP

### Step 1.1: Create Database
First created the `ecommerce` database
```
use ecommerce;
```
This command creates or switches to the ecommerce database.

---

### Step 1.2: Create Collections
Created the four main collections
```
db.createCollection("users");
db.createCollection("categories");
db.createCollection("products");
db.createCollection("orders");
```
![alt text](/asset/image-1.png)

It creates empty collections that will store our e-commerce data.

---

## PART 2: INSERT SAMPLE DATA

### Step 2.1: Insert Users Data
It insert sample users into the users collection.
```
db.users.insertMany([
  {
    name: "Tashi Dorji",
    email: "tashi@example.com",
    phone: "+975-17-123-456",
    address: {
      line1: "Building 12",
      city: "Thimphu",
      country: "Bhutan",
      postalCode: "11001"
    },
    createdAt: new Date("2026-04-18T08:00:00Z")
  },
  {
    name: "Sonam Choden",
    email: "sonam@example.com",
    phone: "+975-17-654-321",
    address: {
      line1: "Flat 3B",
      city: "Phuntsholing",
      country: "Bhutan",
      postalCode: "21001"
    },
    createdAt: new Date("2026-04-19T10:30:00Z")
  }
]);
```
![alt text](/asset/image.png)

Inserted 2 customer records with their contact information and addresses.

---

### Step 2.2: Insert Categories Data
Insert product categories
```
db.categories.insertMany([
  {
    name: "Electronics",
    slug: "electronics",
    parentCategoryId: null
  },
  {
    name: "Accessories",
    slug: "accessories",
    parentCategoryId: null
  }
]);
```
![alt text](/asset/image-2.png)

Inserted product categories like Electronics and Accessories.

---

### Step 2.3: Insert Products Data
Insert product catalog
```
db.products.insertMany([
  {
    name: "Wireless Bluetooth Headphones",
    slug: "wireless-bluetooth-headphones",
    categoryId: ObjectId("000000000000000000000001"),
    price: 129.99,
    currency: "USD",
    stock: 200,
    attributes: {
      brand: "Acme Audio",
      color: "black",
      wireless: true,
      batteryLifeHours: 24
    },
    tags: ["audio", "wireless", "headphones"],
    createdAt: new Date("2026-04-18T10:00:00Z")
  },
  {
    name: "USB-C Cable 1m",
    slug: "usb-c-cable-1m",
    categoryId: ObjectId("000000000000000000000002"),
    price: 9.99,
    currency: "USD",
    stock: 500,
    attributes: {
      brand: "Acme Tech",
      lengthMeters: 1,
      color: "white"
    },
    tags: ["cable", "usb-c"],
    createdAt: new Date("2026-04-18T11:00:00Z")
  },
  {
    name: "Mechanical Keyboard",
    slug: "mechanical-keyboard",
    categoryId: ObjectId("000000000000000000000001"),
    price: 79.99,
    currency: "USD",
    stock: 150,
    attributes: {
      brand: "Acme Input",
      layout: "US",
      switchType: "blue",
      backlight: true
    },
    tags: ["keyboard", "mechanical", "backlit"],
    createdAt: new Date("2026-04-19T09:00:00Z")
  }
]);
```
![alt text](/asset/image-3.png)

Inserted 3 products with different attributes, prices and stock quantities.

---

### Step 2.4: Insert Orders Data
Insert customer orders with line items
```
db.orders.insertMany([
  {
    userId: ObjectId(),
    status: "PAID",
    items: [
      {
        productId: ObjectId("000000000000000000000001"),
        productName: "Wireless Bluetooth Headphones",
        unitPrice: 129.99,
        quantity: 2,
        lineTotal: 259.98
      },
      {
        productId: ObjectId("000000000000000000000002"),
        productName: "USB-C Cable 1m",
        unitPrice: 9.99,
        quantity: 1,
        lineTotal: 9.99
      }
    ],
    grandTotal: 269.97,
    currency: "USD",
    createdAt: new Date("2026-04-19T15:30:00Z"),
    paymentMethod: "CARD"
  },
  {
    userId: ObjectId(),
    status: "PAID",
    items: [
      {
        productId: ObjectId("000000000000000000000003"),
        productName: "Mechanical Keyboard",
        unitPrice: 79.99,
        quantity: 1,
        lineTotal: 79.99
      }
    ],
    grandTotal: 79.99,
    currency: "USD",
    createdAt: new Date("2026-04-20T09:15:00Z"),
    paymentMethod: "COD"
  }
]);
```
![alt text](/asset/image-4.png)

Inserted 2 customer orders. Each order contains multiple items with pricing information.

---

## PART 3: BASIC QUERIES - RETRIEVE DATA

### Query 3.1: Retrieve All Users
View all users in the collection
```
db.users.find().pretty();
```
![alt text](/asset/image-5.png)

It displays all customer records in a readable format.

---

### Query 3.2: Retrieve All Products with Filters
Find products by category and price range
```
db.products.find({
  price: { $gte: 10, $lte: 100 }
}).pretty();
```
![alt text](/asset/image-6.png)

It shows products priced between $10 and $100.

---

### Query 3.3: Retrieve Specific User Orders
Find orders by status
```
db.orders.find({
  status: "PAID"
}).pretty();
```
![alt text](/asset/image-7.png)

It shows all completed/paid orders.

---

## PART 4: AGGREGATION QUERIES - ANALYTICS

### Query 4.1: Daily Sales Totals
Calculate revenue and order count per day
```
db.orders.aggregate([
  {
    $match: { status: "PAID" }
  },
  {
    $group: {
      _id: {
        year: { $year: "$createdAt" },
        month: { $month: "$createdAt" },
        day: { $dayOfMonth: "$createdAt" }
      },
      totalRevenue: { $sum: "$grandTotal" },
      orderCount: { $sum: 1 }
    }
  },
  {
    $project: {
      _id: 0,
      date: {
        $dateFromParts: {
          year: "$_id.year",
          month: "$_id.month",
          day: "$_id.day"
        }
      },
      totalRevenue: 1,
      orderCount: 1
    }
  },
  {
    $sort: { date: 1 }
  }
]);
```
![alt text](/asset/image-8.png)

It shows total revenue and number of orders for each day. Useful for sales tracking.

---

### Query 4.2: Top 5 Products by Revenue
Find products generating most revenue
```
db.orders.aggregate([
  { $match: { status: "PAID" } },
  { $unwind: "$items" },
  {
    $group: {
      _id: "$items.productId",
      productName: { $first: "$items.productName" },
      totalRevenue: { $sum: "$items.lineTotal" },
      totalQuantity: { $sum: "$items.quantity" }
    }
  },
  { $sort: { totalRevenue: -1 } },
  { $limit: 5 }
]);
```
![alt text](/asset/image-9.png)

It shows the top 5 best-selling products by revenue. $unwind breaks down order items, then groups by product.

---

### Query 4.3: Average Order Value per Customer
Calculate customer spending statistics
```
db.orders.aggregate([
  { $match: { status: "PAID" } },
  {
    $group: {
      _id: "$userId",
      totalOrders: { $sum: 1 },
      totalSpent: { $sum: "$grandTotal" },
      minOrderValue: { $min: "$grandTotal" },
      maxOrderValue: { $max: "$grandTotal" },
      avgOrderValue: { $avg: "$grandTotal" }
    }
  },
  {
    $lookup: {
      from: "users",
      localField: "_id",
      foreignField: "_id",
      as: "user"
    }
  },
  { $unwind: "$user" },
  {
    $project: {
      _id: 0,
      userId: "$_id",
      userName: "$user.name",
      totalOrders: 1,
      totalSpent: 1,
      minOrderValue: 1,
      maxOrderValue: 1,
      avgOrderValue: 1
    }
  },
  { $sort: { totalSpent: -1 } }
]);
```
![alt text](/asset/image-10.png)

It shows customer spending patterns. $lookup joins with users collection to show customer names.

---

### Query 4.4: Product Catalog with Category Information
Display products with their categories
```
db.products.aggregate([
  {
    $lookup: {
      from: "categories",
      localField: "categoryId",
      foreignField: "_id",
      as: "category"
    }
  },
  { $unwind: "$category" },
  {
    $project: {
      _id: 0,
      name: 1,
      price: 1,
      stock: 1,
      brand: "$attributes.brand",
      color: "$attributes.color",
      categoryName: "$category.name"
    }
  },
  { $sort: { categoryName: 1, name: 1 } }
]);
```
![alt text](/asset/image-11.png)

It shows product details with category names using $lookup to join categories collection.

---

## PART 5: INDEXING - PERFORMANCE OPTIMIZATION

### Query 5.1: Create Index for Orders by User and Date
Index for retrieving user orders sorted by date
```
db.orders.createIndex(
  { userId: 1, createdAt: -1 },
  { name: "idx_orders_user_createdAt" }
);
```
![alt text](/asset/image-12.png)

This index speeds up queries that filter orders by user and sort by creation date.

---

### Query 5.2: Create Compound Index for Status and Date (ESR Rule)
Index following Equality-Sort-Range pattern
```
db.orders.createIndex(
  { status: 1, createdAt: -1, grandTotal: 1 },
  { name: "idx_orders_status_createdAt_grandTotal" }
);
```
![alt text](/asset/image-13.png)

It supports queries filtering by status and date range. Field order matters for performance.

---

### Query 5.3: Create Index for Products by Category and Price
Speed up product browsing queries
```
db.products.createIndex(
  { categoryId: 1, price: 1 },
  { name: "idx_products_category_price" }
);
```
![alt text](/asset/image-14.png)
![alt text](/asset/image-16.png)

It helps queries that filter products by category and sort by price.

---

### Query 5.4: Create Text Index for Product Search
Enable full-text search on products
```
db.products.createIndex(
  { name: "text", tags: "text" },
  { 
    name: "idx_products_text",
    weights: { name: 10, tags: 5 }
  }
);
```
![alt text](/asset/image-15.png)

It enables searching products by keywords in name and tags with weighted importance.

---

### Query 5.5: Text Search Example
Search for wireless products
```
db.products.find(
  { $text: { $search: "wireless keyboard" } },
  { score: { $meta: "textScore" }, name: 1, price: 1 }
).sort({ score: { $meta: "textScore" } });
```
![alt text](/asset/image-17.png)

It searches products containing "wireless" or "keyboard", ranked by relevance score.

---

## PART 6: QUERY ANALYSIS - EXPLAIN

### Query 6.1: Analyze Query BEFORE Creating Index
Check query performance without index
```
db.orders.find(
  { status: "PAID", createdAt: { $gte: new Date("2026-04-19") } }
).sort({ createdAt: -1 }).explain("executionStats");
```
![alt text](/asset/image-18.png)
![alt text](/asset/image-19.png)

It shows the query plan. Look for "COLLSCAN" (slow - scans all documents) vs "IXSCAN" (fast - uses index).

---

### Query 6.2: Analyze Query AFTER Creating Index
Run explain again after index creation to see improvement
```
db.orders.find(
  { status: "PAID", createdAt: { $gte: new Date("2026-04-19") } }
).sort({ createdAt: -1 }).explain("executionStats");
```
![alt text](/asset/image-20.png)
![alt text](/asset/image-21.png)

It should now show "IXSCAN" and much lower "totalDocsExamined" count - indicating index is being used.

---

## PART 7: ADDITIONAL USEFUL QUERIES

### Query 7.1: View All Indexes on a Collection
List indexes created on orders collection
```
db.orders.getIndexes();
```
![alt text](/asset/image-22.png)

It shows all indexes created with their field specifications.

---

### Query 7.2: Delete an Index
Remove an unused index
```
db.orders.dropIndex("idx_orders_user_createdAt");
```
![alt text](/asset/image-23.png)

It removes the index to free up space and reduce write overhead.

---

### Query 7.3: Count Total Orders by Status
Quick statistics query
```javascript
db.orders.aggregate([
  {
    $group: {
      _id: "$status",
      count: { $sum: 1 }
    }
  }
]);
```
![alt text](/asset/image-24.png)

It shows count of orders in each status (PAID, PENDING, SHIPPED, CANCELLED).

---

### Query 7.4: Total Revenue Across All Orders
Business summary metric
```
db.orders.aggregate([
  { $match: { status: "PAID" } },
  {
    $group: {
      _id: null,
      totalRevenue: { $sum: "$grandTotal" },
      avgOrderValue: { $avg: "$grandTotal" },
      totalOrders: { $sum: 1 }
    }
  }
]);
```
![alt text](/asset/image-25.png)

It shows overall business metrics - total revenue, average order value, and order count.

---

### Query 7.5: Find Orders with Multiple Items
Identify bulk orders
```
db.orders.aggregate([
  {
    $project: {
      _id: 1,
      userId: 1,
      createdAt: 1,
      itemCount: { $size: "$items" },
      grandTotal: 1
    }
  },
  {
    $match: { itemCount: { $gt: 1 } }
  },
  { $sort: { grandTotal: -1 } }
]);
```
![alt text](/asset/image-26.png)

It shows orders containing 2 or more items, sorted by total amount.


# Common Mistakes and How to Avoid Them

## Designing the Schema As If It Were a Relational Database

**Mistake:** Over-relying on `$lookup`, similar to foreign key relationships in relational databases, where there are too many collections involved.

**Correction:** Embed documents when they are highly related and always fetched in one request (for example, putting order items within orders).

## Unlimited Document Growth

**Mistake:** Repeatedly adding sub-documents to an array in a document (like never-ending history) that can be unreasonably long.

**Correction:** Splitting the documents into different documents or even collections when the arrays are potentially unlimited.

## No Indexes for Common Queries

**Mistake:** Using $filter and sort operations on large collections without indexing, resulting in `COLLSCAN`.

**Correction:** Recognizing frequent requests, creating appropriate indexes, and checking through `explain("executionStats")`.

## Inefficient Compound Index Ordering

**Mistake:** Ordering index fields incorrectly, causing partial index usage or no benefit.

**Fix:** Follow patterns like ESR (Equality → Sort → Range) and ensure filters and sorts are aligned with index order.

## Over‑Indexing

**Mistake:** Creating too many indexes, leading to heavy write overhead and large index storage.

**Fix:** Only index fields required for important queries; drop unused indexes based on performance profiling and index statistics.

## Ignoring Query Plans

**Mistake:** Assuming queries are using indexes without checking.

**Fix:** Regularly inspect `explain()` outputs and, if needed, use `index hints` selectively for testing.

# Conclusion

This practical saw me implement a MongoDB schema for an e-commerce site following the query-first approach. This involved creating four collections; users, categories, products, and orders, while making careful decisions about either embedding or referencing specific documents.

I built several non-trivial pipelines through which I was able to calculate daily sales, top products by total revenue, average order value per user, and view catalog products with their respective categories. Such processes involved the use of `$group`, `$unwind`, `$lookup` and `$project`.

The most crucial part of the process came when I optimized my MongoDB schema by building various types of indexes such as `single index`, `compound index` and `text index`. For instance, `userId` and `createdAt` made up of the `single index` that could allow a user to see his/her order history while `{ status: 1, createdAt: -1}` formed a `compound index` which would facilitate searches based on different statuses and creation date. The `explain("executionStats")` function helped me to verify the change from `COLLSCAN` to `IXSCAN`, fewer `totalDocsExamined` values and less time.

Anti-patterns avoided include over-embedding documents, uncontrolled growth, lack of indexes and wrong order of indexes. The attribute pattern on products helped demonstrate the usefulness of MongoDB in storing heterogeneous data.

---



