"""
Vault Vectors - ChromaDB wrapper for semantic search

Provides vector storage and similarity search for the Vault 2.0 platform.
Uses OpenAI embeddings and ChromaDB for persistent storage.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from .config import (
        VECTORS_PATH, EMBEDDING_MODEL,
        OPENAI_API_KEY, CHROMA_COLLECTIONS,
        CHUNK_MAX_TOKENS, CHUNK_OVERLAP_TOKENS, CHUNK_THRESHOLD_TOKENS,
        HYBRID_VECTOR_WEIGHT, HYBRID_TEXT_WEIGHT
    )
except ImportError:
    from config import (
        VECTORS_PATH, EMBEDDING_MODEL,
        OPENAI_API_KEY, CHROMA_COLLECTIONS,
        CHUNK_MAX_TOKENS, CHUNK_OVERLAP_TOKENS, CHUNK_THRESHOLD_TOKENS,
        HYBRID_VECTOR_WEIGHT, HYBRID_TEXT_WEIGHT
    )

logger = logging.getLogger(__name__)


class VaultVectors:
    """ChromaDB wrapper for Vault semantic search."""

    def __init__(self, persist_directory: Optional[Path] = None):
        """Initialize the vector store."""
        if not CHROMADB_AVAILABLE:
            raise ImportError("chromadb is required. Install with: pip install chromadb")

        self.persist_directory = persist_directory or VECTORS_PATH
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB with persistent storage
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )

        # Initialize OpenAI client if available
        self.openai_client = None
        if OPENAI_AVAILABLE and OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

        # Collection cache
        self._collections = {}

    def _get_collection(self, name: str) -> Any:
        """Get or create a collection."""
        if name not in self._collections:
            self._collections[name] = self.client.get_or_create_collection(
                name=name,
                metadata={"description": CHROMA_COLLECTIONS.get(name, "")}
            )
        return self._collections[name]

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI."""
        if not self.openai_client:
            raise RuntimeError("OpenAI client not available. Set OPENAI_API_KEY environment variable.")

        response = self.openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts using OpenAI."""
        if not self.openai_client:
            raise RuntimeError("OpenAI client not available. Set OPENAI_API_KEY environment variable.")

        response = self.openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts
        )
        return [item.embedding for item in response.data]

    # ===========================================
    # DOCUMENT OPERATIONS
    # ===========================================

    def add_document(
        self,
        doc_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a document to the vector store."""
        collection = self._get_collection("documents")

        # Generate embedding
        embedding = self.embed_text(content)

        # Prepare metadata
        meta = metadata or {}
        meta["indexed_at"] = datetime.now().isoformat()

        collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[meta]
        )

        return doc_id

    def query_documents(
        self,
        query: str,
        n_results: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query documents by semantic similarity."""
        collection = self._get_collection("documents")

        # Generate query embedding
        query_embedding = self.embed_text(query)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata
        )

        # Format results
        formatted = []
        if results and results['ids'] and results['ids'][0]:
            for i, doc_id in enumerate(results['ids'][0]):
                formatted.append({
                    'id': doc_id,
                    'document': results['documents'][0][i] if results['documents'] else None,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results.get('distances') else None
                })

        return formatted

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the vector store."""
        collection = self._get_collection("documents")
        collection.delete(ids=[doc_id])
        return True

    # ===========================================
    # CHUNK OPERATIONS
    # ===========================================

    def add_chunk(
        self,
        chunk_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a document chunk to the vector store."""
        collection = self._get_collection("chunks")

        # Generate embedding
        embedding = self.embed_text(content)

        # Prepare metadata
        meta = metadata or {}
        meta["indexed_at"] = datetime.now().isoformat()

        collection.add(
            ids=[chunk_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[meta]
        )

        return chunk_id

    def add_chunks_batch(
        self,
        chunks: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Add multiple chunks in a batch.

        Each chunk dict should have: id, content, metadata
        """
        if not chunks:
            return []

        collection = self._get_collection("chunks")

        ids = [c['id'] for c in chunks]
        contents = [c['content'] for c in chunks]
        metadatas = []

        for c in chunks:
            meta = c.get('metadata', {})
            meta["indexed_at"] = datetime.now().isoformat()
            metadatas.append(meta)

        # Batch embed all content
        embeddings = self.embed_texts(contents)

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas
        )

        return ids

    def query_chunks(
        self,
        query: str,
        n_results: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query chunks by semantic similarity."""
        collection = self._get_collection("chunks")

        # Generate query embedding
        query_embedding = self.embed_text(query)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata
        )

        # Format results
        formatted = []
        if results and results['ids'] and results['ids'][0]:
            for i, chunk_id in enumerate(results['ids'][0]):
                formatted.append({
                    'id': chunk_id,
                    'document': results['documents'][0][i] if results['documents'] else None,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results.get('distances') else None
                })

        return formatted

    def delete_chunks_by_document(self, doc_id: int) -> bool:
        """Delete all chunks for a document."""
        collection = self._get_collection("chunks")

        # Delete by metadata filter
        # ChromaDB may raise ValueError if no matching documents found
        try:
            collection.delete(where={"document_id": doc_id})
            return True
        except ValueError as e:
            # No documents matched the filter - this is OK, nothing to delete
            logger.debug(f"No chunks found for doc {doc_id}: {e}")
            return True

    def hybrid_search(
        self,
        query: str,
        n_results: int = 10,
        vector_weight: Optional[float] = None,
        text_weight: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining vector similarity and FTS5 BM25.

        Args:
            query: Search query
            n_results: Number of results to return
            vector_weight: Weight for vector scores (default from config)
            text_weight: Weight for BM25 scores (default from config)

        Returns:
            List of results with combined scores
        """
        try:
            from .db import search_chunks_fts, get_chunk_by_id
        except ImportError:
            from db import search_chunks_fts, get_chunk_by_id

        vector_weight = vector_weight or HYBRID_VECTOR_WEIGHT
        text_weight = text_weight or HYBRID_TEXT_WEIGHT

        # Get vector search results (more than needed for merging)
        vector_results = self.query_chunks(query, n_results=n_results * 2)

        # Get FTS5 BM25 results
        fts_results = search_chunks_fts(query, limit=n_results * 2)

        # Build score maps
        # Vector distance: lower is better, normalize to 0-1 score where higher is better
        vector_scores = {}
        if vector_results:
            max_dist = max(r['distance'] for r in vector_results) or 1
            min_dist = min(r['distance'] for r in vector_results) or 0
            dist_range = max_dist - min_dist or 1

            for r in vector_results:
                # Normalize: convert distance to similarity (1 - normalized_distance)
                normalized_dist = (r['distance'] - min_dist) / dist_range
                score = 1 - normalized_dist
                # Extract chunk_id from vector id (format: "chunk_N")
                chunk_id = r['id'].replace('chunk_', '') if r['id'].startswith('chunk_') else r['id']
                vector_scores[chunk_id] = {
                    'score': score,
                    'data': r
                }

        # BM25: lower is better in SQLite FTS5, normalize similarly
        bm25_scores = {}
        if fts_results:
            # BM25 scores are negative in SQLite, more negative = better match
            # Convert to positive scale where higher is better
            scores = [abs(r['bm25_score']) for r in fts_results]
            max_score = max(scores) or 1
            min_score = min(scores) or 0
            score_range = max_score - min_score or 1

            for r in fts_results:
                # Normalize and invert
                abs_score = abs(r['bm25_score'])
                normalized = (abs_score - min_score) / score_range
                score = 1 - normalized  # Higher original (less negative) = better
                chunk_id = str(r['id'])
                bm25_scores[chunk_id] = {
                    'score': score,
                    'data': r
                }

        # Merge scores
        all_chunk_ids = set(vector_scores.keys()) | set(bm25_scores.keys())
        combined = []

        for chunk_id in all_chunk_ids:
            vec_score = vector_scores.get(chunk_id, {}).get('score', 0)
            bm25_score = bm25_scores.get(chunk_id, {}).get('score', 0)

            final_score = (vec_score * vector_weight) + (bm25_score * text_weight)

            # Get chunk data from whichever source has it
            if chunk_id in vector_scores:
                data = vector_scores[chunk_id]['data']
                chunk_data = {
                    'chunk_id': chunk_id,
                    'content': data.get('document'),
                    'metadata': data.get('metadata', {}),
                    'vector_score': vec_score,
                    'bm25_score': bm25_score,
                    'combined_score': final_score
                }
            else:
                data = bm25_scores[chunk_id]['data']
                chunk_data = {
                    'chunk_id': chunk_id,
                    'content': data.get('content'),
                    'metadata': {
                        'document_id': data.get('document_id'),
                        'doc_title': data.get('doc_title'),
                        'doc_path': data.get('doc_path'),
                        'doc_type': data.get('doc_type'),
                        'start_line': data.get('start_line'),
                        'end_line': data.get('end_line')
                    },
                    'vector_score': vec_score,
                    'bm25_score': bm25_score,
                    'combined_score': final_score
                }

            combined.append(chunk_data)

        # Sort by combined score (higher is better)
        combined.sort(key=lambda x: x['combined_score'], reverse=True)

        return combined[:n_results]

    def index_document_chunks(
        self,
        document_id: int,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Chunk a document and index all chunks.

        Args:
            document_id: The document ID in the database
            content: Full document content
            metadata: Additional metadata for all chunks

        Returns:
            List of chunk vector IDs
        """
        try:
            from .chunker import chunk_document, should_chunk
            from .db import add_chunk, delete_chunks_for_document, update_chunk_vector_id
        except ImportError:
            from chunker import chunk_document, should_chunk
            from db import add_chunk, delete_chunks_for_document, update_chunk_vector_id

        # Delete existing chunks for this document
        delete_chunks_for_document(document_id)
        self.delete_chunks_by_document(document_id)

        # Check if document needs chunking
        if not should_chunk(content, CHUNK_THRESHOLD_TOKENS):
            # Small document - store as single chunk
            chunks = [{
                'text': content,
                'content_hash': '',
                'start_line': 1,
                'end_line': content.count('\n') + 1,
                'token_count': 0,
                'chunk_index': 0
            }]
        else:
            # Chunk the document
            chunk_objs = chunk_document(
                content,
                max_tokens=CHUNK_MAX_TOKENS,
                overlap_tokens=CHUNK_OVERLAP_TOKENS
            )
            chunks = [
                {
                    'text': c.text,
                    'content_hash': c.content_hash,
                    'start_line': c.start_line,
                    'end_line': c.end_line,
                    'token_count': c.token_count,
                    'chunk_index': c.chunk_index
                }
                for c in chunk_objs
            ]

        # Prepare batch for vector indexing
        batch = []
        db_chunk_ids = []

        base_meta = metadata or {}

        for chunk in chunks:
            # Add to SQLite
            chunk_id = add_chunk(
                document_id=document_id,
                content=chunk['text'],
                content_hash=chunk['content_hash'],
                start_line=chunk['start_line'],
                end_line=chunk['end_line'],
                chunk_index=chunk['chunk_index']
            )
            db_chunk_ids.append(chunk_id)

            # Prepare for vector store
            chunk_meta = base_meta.copy()
            chunk_meta['document_id'] = document_id
            chunk_meta['start_line'] = chunk['start_line']
            chunk_meta['end_line'] = chunk['end_line']
            chunk_meta['chunk_index'] = chunk['chunk_index']

            batch.append({
                'id': f"chunk_{chunk_id}",
                'content': chunk['text'],
                'metadata': chunk_meta
            })

        # Index all chunks in vector store
        vector_ids = self.add_chunks_batch(batch)

        # Update SQLite with vector IDs
        for db_id, vec_id in zip(db_chunk_ids, vector_ids):
            update_chunk_vector_id(db_id, vec_id)

        return vector_ids

    # ===========================================
    # FACTS OPERATIONS
    # ===========================================

    def add_fact(
        self,
        fact_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a fact to the vector store."""
        collection = self._get_collection("facts")

        embedding = self.embed_text(content)

        meta = metadata or {}
        meta["indexed_at"] = datetime.now().isoformat()

        collection.add(
            ids=[fact_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[meta]
        )

        return fact_id

    def query_facts(
        self,
        query: str,
        n_results: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query facts by semantic similarity."""
        collection = self._get_collection("facts")

        query_embedding = self.embed_text(query)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata
        )

        formatted = []
        if results and results['ids'] and results['ids'][0]:
            for i, fact_id in enumerate(results['ids'][0]):
                formatted.append({
                    'id': fact_id,
                    'document': results['documents'][0][i] if results['documents'] else None,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results.get('distances') else None
                })

        return formatted

    # ===========================================
    # IDEAS OPERATIONS
    # ===========================================

    def add_idea(
        self,
        idea_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add an idea to the vector store."""
        collection = self._get_collection("ideas")

        embedding = self.embed_text(content)

        meta = metadata or {}
        meta["indexed_at"] = datetime.now().isoformat()

        collection.add(
            ids=[idea_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[meta]
        )

        return idea_id

    def query_ideas(
        self,
        query: str,
        n_results: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query ideas by semantic similarity."""
        collection = self._get_collection("ideas")

        query_embedding = self.embed_text(query)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata
        )

        formatted = []
        if results and results['ids'] and results['ids'][0]:
            for i, idea_id in enumerate(results['ids'][0]):
                formatted.append({
                    'id': idea_id,
                    'document': results['documents'][0][i] if results['documents'] else None,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results.get('distances') else None
                })

        return formatted

    def find_similar_ideas(self, idea_id: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Find ideas similar to a given idea."""
        collection = self._get_collection("ideas")

        # Get the original idea
        result = collection.get(ids=[idea_id], include=["embeddings"])

        if not result or not result['embeddings']:
            return []

        # Query with its embedding
        results = collection.query(
            query_embeddings=result['embeddings'],
            n_results=n_results + 1  # Include extra since we'll filter out self
        )

        formatted = []
        if results and results['ids'] and results['ids'][0]:
            for i, found_id in enumerate(results['ids'][0]):
                if found_id != idea_id:  # Skip self
                    formatted.append({
                        'id': found_id,
                        'document': results['documents'][0][i] if results['documents'] else None,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results.get('distances') else None
                    })

        return formatted[:n_results]

    # ===========================================
    # HEALTH OPERATIONS
    # ===========================================

    def add_health_entry(
        self,
        entry_id: str,
        summary: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a health entry summary to the vector store."""
        collection = self._get_collection("health")

        embedding = self.embed_text(summary)

        meta = metadata or {}
        meta["indexed_at"] = datetime.now().isoformat()

        collection.add(
            ids=[entry_id],
            embeddings=[embedding],
            documents=[summary],
            metadatas=[meta]
        )

        return entry_id

    def query_health(
        self,
        query: str,
        n_results: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query health entries by semantic similarity."""
        collection = self._get_collection("health")

        query_embedding = self.embed_text(query)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata
        )

        formatted = []
        if results and results['ids'] and results['ids'][0]:
            for i, entry_id in enumerate(results['ids'][0]):
                formatted.append({
                    'id': entry_id,
                    'document': results['documents'][0][i] if results['documents'] else None,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results.get('distances') else None
                })

        return formatted

    # ===========================================
    # UNIFIED OPERATIONS
    # ===========================================

    def semantic_search(
        self,
        query: str,
        collections: Optional[List[str]] = None,
        n_results: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Search across multiple collections."""
        if collections is None:
            collections = list(CHROMA_COLLECTIONS.keys())

        results = {}
        query_embedding = self.embed_text(query)

        for coll_name in collections:
            try:
                collection = self._get_collection(coll_name)
                coll_results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results
                )

                formatted = []
                if coll_results and coll_results['ids'] and coll_results['ids'][0]:
                    for i, item_id in enumerate(coll_results['ids'][0]):
                        formatted.append({
                            'id': item_id,
                            'document': coll_results['documents'][0][i] if coll_results['documents'] else None,
                            'metadata': coll_results['metadatas'][0][i] if coll_results['metadatas'] else {},
                            'distance': coll_results['distances'][0][i] if coll_results.get('distances') else None
                        })

                results[coll_name] = formatted
            except ValueError as e:
                # Collection may be empty or query invalid
                logger.debug(f"No results from collection {coll_name}: {e}")
                results[coll_name] = []

        return results

    def get_stats(self) -> Dict[str, int]:
        """Get counts for each collection."""
        stats = {}
        for coll_name in CHROMA_COLLECTIONS.keys():
            try:
                collection = self._get_collection(coll_name)
                stats[coll_name] = collection.count()
            except ValueError as e:
                # Collection may not exist yet
                logger.debug(f"Collection {coll_name} not ready: {e}")
                stats[coll_name] = 0
        return stats


# Singleton instance
_vault_vectors = None


def get_vault_vectors() -> VaultVectors:
    """Get the singleton VaultVectors instance."""
    global _vault_vectors
    if _vault_vectors is None:
        _vault_vectors = VaultVectors()
    return _vault_vectors
