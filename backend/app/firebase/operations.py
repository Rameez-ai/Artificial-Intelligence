"""
Smart Loan AI - Firebase CRUD Operations
==========================================
Generic Firestore operations for all collections.
"""

from datetime import datetime
from typing import Optional
from firebase.client import get_db


class FirebaseOperations:
    """Generic Firestore CRUD operations."""

    # In-memory fallback storage when Firebase is not configured
    _mock_store = {}

    @staticmethod
    def _get_collection(collection_name):
        db = get_db()
        if db is None:
            return None
        return db.collection(collection_name)

    @classmethod
    def create(cls, collection: str, data: dict, doc_id: str = None) -> str:
        """Create a document in Firestore."""
        data['created_at'] = datetime.utcnow().isoformat()
        data['updated_at'] = datetime.utcnow().isoformat()

        col = cls._get_collection(collection)
        if col is None:
            # Mock mode
            if collection not in cls._mock_store:
                cls._mock_store[collection] = {}
            if doc_id is None:
                doc_id = f"mock_{len(cls._mock_store[collection]) + 1}"
            data['id'] = doc_id
            cls._mock_store[collection][doc_id] = data
            return doc_id

        if doc_id:
            col.document(doc_id).set(data)
            return doc_id
        else:
            doc_ref = col.add(data)
            return doc_ref[1].id

    @classmethod
    def get(cls, collection: str, doc_id: str) -> Optional[dict]:
        """Get a document by ID."""
        col = cls._get_collection(collection)
        if col is None:
            store = cls._mock_store.get(collection, {})
            return store.get(doc_id)

        doc = col.document(doc_id).get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None

    @classmethod
    def get_all(cls, collection: str, limit: int = 100) -> list:
        """Get all documents in a collection."""
        col = cls._get_collection(collection)
        if col is None:
            store = cls._mock_store.get(collection, {})
            return list(store.values())[:limit]

        docs = col.limit(limit).stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            results.append(data)
        return results

    @classmethod
    def query(cls, collection: str, field: str, operator: str, value, limit: int = 100) -> list:
        """Query documents with a filter."""
        col = cls._get_collection(collection)
        if col is None:
            store = cls._mock_store.get(collection, {})
            results = []
            for doc in store.values():
                if field in doc:
                    if operator == '==' and doc[field] == value:
                        results.append(doc)
                    elif operator == '>' and doc[field] > value:
                        results.append(doc)
                    elif operator == '<' and doc[field] < value:
                        results.append(doc)
            return results[:limit]

        docs = col.where(field, operator, value).limit(limit).stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            results.append(data)
        return results

    @classmethod
    def update(cls, collection: str, doc_id: str, data: dict) -> bool:
        """Update a document."""
        data['updated_at'] = datetime.utcnow().isoformat()

        col = cls._get_collection(collection)
        if col is None:
            store = cls._mock_store.get(collection, {})
            if doc_id in store:
                store[doc_id].update(data)
                return True
            return False

        col.document(doc_id).update(data)
        return True

    @classmethod
    def delete(cls, collection: str, doc_id: str) -> bool:
        """Delete a document."""
        col = cls._get_collection(collection)
        if col is None:
            store = cls._mock_store.get(collection, {})
            if doc_id in store:
                del store[doc_id]
                return True
            return False

        col.document(doc_id).delete()
        return True

    @classmethod
    def count(cls, collection: str) -> int:
        """Count documents in a collection."""
        col = cls._get_collection(collection)
        if col is None:
            return len(cls._mock_store.get(collection, {}))
        return len(list(col.stream()))
