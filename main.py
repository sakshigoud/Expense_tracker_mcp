from fastmcp import FastMCP
import os
from pymongo import ASCENDING, MongoClient

CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "expense_tracker")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "expenses")

mcp = FastMCP("ExpenseTracker")
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client[MONGODB_DB]
expenses_collection = db[MONGODB_COLLECTION]

def init_db():
    # Create indexes once at startup for faster range and category queries.
    expenses_collection.create_index([("date", ASCENDING)])
    expenses_collection.create_index([("category", ASCENDING), ("date", ASCENDING)])

init_db()

@mcp.tool()
def add_expense(date, amount, category, subcategory="", note=""):
    '''Add a new expense entry to the database.'''
    doc = {
        "date": date,
        "amount": float(amount),
        "category": category,
        "subcategory": subcategory,
        "note": note,
    }
    result = expenses_collection.insert_one(doc)
    return {"status": "ok", "id": str(result.inserted_id)}
    
@mcp.tool()
def list_expenses(start_date, end_date):
    '''List expense entries within an inclusive date range.'''
    docs = expenses_collection.find(
        {"date": {"$gte": start_date, "$lte": end_date}},
        {"date": 1, "amount": 1, "category": 1, "subcategory": 1, "note": 1},
    ).sort([("date", ASCENDING), ("_id", ASCENDING)])

    return [
        {
            "id": str(doc["_id"]),
            "date": doc.get("date", ""),
            "amount": doc.get("amount", 0),
            "category": doc.get("category", ""),
            "subcategory": doc.get("subcategory", ""),
            "note": doc.get("note", ""),
        }
        for doc in docs
    ]

@mcp.tool()
def summarize(start_date, end_date, category=None):
    '''Summarize expenses by category within an inclusive date range.'''
    match_filter = {"date": {"$gte": start_date, "$lte": end_date}}
    if category:
        match_filter["category"] = category

    pipeline = [
        {"$match": match_filter},
        {
            "$group": {
                "_id": "$category",
                "total_amount": {"$sum": "$amount"},
            }
        },
        {"$project": {"_id": 0, "category": "$_id", "total_amount": 1}},
        {"$sort": {"category": 1}},
    ]

    return list(expenses_collection.aggregate(pipeline))

@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    # Read fresh each time so you can edit the file without restarting
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    mcp.run()
