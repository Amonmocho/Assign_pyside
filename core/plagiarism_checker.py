from .embedder import get_embedding, similarity

class PlagiarismChecker:
    def __init__(self, reference_texts: dict[str, str], threshold: float = 0.75):
        """
        :param reference_texts: dict of name → raw text  
        :param threshold: minimum cosine‐similarity to flag (0–1)
        """
        self.threshold = threshold
        # Precompute all reference embeddings
        self.refs = {
            name: get_embedding(txt)
            for name, txt in reference_texts.items()
        }

    def check(self, text: str) -> dict[str, float]:
        """
        Compute similarity of `text` to each reference.
        Returns a dict {ref_name: score} for score >= threshold,
        sorted descending by score.
        """
        emb = get_embedding(text)
        results = {}
        for name, ref_emb in self.refs.items():
            score = similarity(emb, ref_emb)
            if score >= self.threshold:
                results[name] = score
        # sort by score descending
        return dict(sorted(results.items(), key=lambda kv: kv[1], reverse=True))


# quick sanity test if run directly
if __name__ == "__main__":
    sample = {"foo.txt":"bar baz qux", "lorem.txt":"ipsum dolor sit amet"}
    pc = PlagiarismChecker(sample, threshold=0.2)
    print(pc.check("bar baz"))   # Expect to see foo.txt flagged
