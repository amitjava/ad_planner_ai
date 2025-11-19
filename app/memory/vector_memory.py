"""Vector Memory using ChromaDB"""
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from typing import List, Dict, Any, Optional
import json
from pathlib import Path


class VectorMemory:
    """Manages vector embeddings for long-term memory"""

    def __init__(self, persist_directory: str = "./vector_store"):
        """Initialize ChromaDB client if available"""
        if not CHROMADB_AVAILABLE:
            print("Warning: ChromaDB not available. Vector memory features will be disabled.")
            self.client = None
            self.user_memory = None
            self.plan_memory = None
            self.feedback_memory = None
            return

        Path(persist_directory).mkdir(parents=True, exist_ok=True)

        # Use PersistentClient for proper persistence
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Create collections
        self.user_memory = self._get_or_create_collection("user_memory")
        self.plan_memory = self._get_or_create_collection("plan_memory")
        self.feedback_memory = self._get_or_create_collection("feedback_memory")

    def _get_or_create_collection(self, name: str):
        """Get or create a collection"""
        if not CHROMADB_AVAILABLE or self.client is None:
            return None
        try:
            return self.client.get_collection(name=name)
        except:
            return self.client.create_collection(
                name=name,
                metadata={"description": f"Collection for {name}"}
            )

    def store_business_profile(self, session_id: str, profile: Dict[str, Any]):
        """Store business profile with embeddings"""
        if not CHROMADB_AVAILABLE or self.user_memory is None:
            return

        document = f"""
        Business: {profile.get('business_name')}
        Type: {profile.get('business_type')}
        Location: {profile.get('location')}
        Goal: {profile.get('goal')}
        Budget: ${profile.get('monthly_budget')}
        Competitors: {', '.join(profile.get('competitors', []))}
        """

        self.user_memory.add(
            documents=[document],
            metadatas=[{"session_id": session_id, "type": "profile"}],
            ids=[f"profile_{session_id}"]
        )

    def store_plan(self, session_id: str, plan_id: str, plan: Dict[str, Any]):
        """Store generated plan"""
        if not CHROMADB_AVAILABLE or self.plan_memory is None:
            return

        document = json.dumps(plan, indent=2)

        self.plan_memory.add(
            documents=[document],
            metadatas=[{"session_id": session_id, "plan_id": plan_id}],
            ids=[f"plan_{plan_id}"]
        )

    def store_feedback(self, session_id: str, plan_type: str, rating: int, feedback_text: str = ""):
        """Store user feedback"""
        if not CHROMADB_AVAILABLE or self.feedback_memory is None:
            return

        document = f"Plan type: {plan_type}, Rating: {rating}/5, Feedback: {feedback_text}"

        self.feedback_memory.add(
            documents=[document],
            metadatas=[{"session_id": session_id, "plan_type": plan_type, "rating": rating}],
            ids=[f"feedback_{session_id}_{plan_type}"]
        )

    def query_similar_profiles(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Find similar business profiles"""
        if not CHROMADB_AVAILABLE or self.user_memory is None:
            return []

        results = self.user_memory.query(
            query_texts=[query_text],
            n_results=n_results
        )

        if results and results['documents']:
            return [
                {
                    "document": doc,
                    "metadata": meta,
                    "distance": dist
                }
                for doc, meta, dist in zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )
            ]
        return []

    def query_similar_plans(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Find similar plans"""
        if not CHROMADB_AVAILABLE or self.plan_memory is None:
            return []

        results = self.plan_memory.query(
            query_texts=[query_text],
            n_results=n_results
        )

        if results and results['documents']:
            return [
                {
                    "document": doc,
                    "metadata": meta,
                    "distance": dist
                }
                for doc, meta, dist in zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )
            ]
        return []

    def get_profile_history(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get profile for a session"""
        if not CHROMADB_AVAILABLE or self.user_memory is None:
            return None

        try:
            result = self.user_memory.get(
                ids=[f"profile_{session_id}"]
            )
            if result and result['documents']:
                return {
                    "document": result['documents'][0],
                    "metadata": result['metadatas'][0]
                }
        except:
            pass
        return None

    def get_feedback_stats(self) -> Dict[str, Any]:
        """Get feedback statistics"""
        if not CHROMADB_AVAILABLE or self.feedback_memory is None:
            return {"total_feedback": 0, "avg_rating": 0, "rating_distribution": {}}

        try:
            all_feedback = self.feedback_memory.get()
            if all_feedback and all_feedback['metadatas']:
                ratings = [m.get('rating', 0) for m in all_feedback['metadatas']]
                return {
                    "total_feedback": len(ratings),
                    "avg_rating": sum(ratings) / len(ratings) if ratings else 0,
                    "rating_distribution": {
                        str(i): ratings.count(i) for i in range(1, 6)
                    }
                }
        except:
            pass
        return {"total_feedback": 0, "avg_rating": 0, "rating_distribution": {}}
