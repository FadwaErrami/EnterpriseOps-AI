
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


RUNBOOKS_DIR = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "runbooks"
)


class RAGService:

    def __init__(self):
        self.documents = []
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            strip_accents="unicode",
        )
        self.document_vectors = None

        self.load_runbooks()

    def load_runbooks(self):
        self.documents = []

        for file_path in sorted(RUNBOOKS_DIR.glob("*.md")):
            content = file_path.read_text(encoding="utf-8")

            if content.strip():
                self.documents.append({
                    "source": file_path.name,
                    "content": content,
                })

        if not self.documents:
            self.document_vectors = None
            return

        texts = [
            document["content"]
            for document in self.documents
        ]

        self.document_vectors = self.vectorizer.fit_transform(texts)

    def search(self, query, top_k=3):
        if not query or not query.strip():
            return []

        if self.document_vectors is None:
            return []

        query_vector = self.vectorizer.transform([query])

        scores = cosine_similarity(
            query_vector,
            self.document_vectors,
        )[0]

        ranked_indices = scores.argsort()[::-1][:top_k]

        results = []

        for index in ranked_indices:
            score = float(scores[index])

            if score <= 0:
                continue

            document = self.documents[index]

            results.append({
                "source": document["source"],
                "score": round(score, 4),
                "content": document["content"],
            })

        return results


rag_service = RAGService()
