// Create the database
db = db.getSiblingDB("matchingservice");

// Create a default admin user
db.createUser({
  user: "admin",
  pwd: "changeme",
  roles: [{ role: "readWrite", db: "matchingservice" }]
});

// Create collections and indexes
db.createCollection("users");
db.users.createIndex({ username: 1 }, { unique: true });

db.createCollection("topics");
db.topics.createIndex({ topic: 1 }, { unique: true });

db.createCollection("subscriptions");
db.subscriptions.createIndex({ user_id: 1 });

db.createCollection("publishers");
db.publishers.createIndex({ "location": "2dsphere" });

db.createCollection("metrics");
db.metrics.createIndex({ topic: 1 });
db.metrics.createIndex({ timestamp: -1 });
