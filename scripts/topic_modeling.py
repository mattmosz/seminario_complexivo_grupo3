import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation


def extract_topics(df: pd.DataFrame,
                   text_column: str = "review_text",
                   n_topics: int = 8,
                   max_features: int = 6000,
                   max_df: float = 0.92,
                   min_df: int = 20,
                   n_top_words: int = 12,
                   random_state: int = 42,
                   max_iter: int = 15) -> list:
    
    # Extrae tópicos de textos usando LDA.
    
    print(f"Extrayendo {n_topics} tópicos del texto...")
    
    # Preparar textos
    texts = df[text_column].fillna("").astype(str).tolist()
    
    # Vectorizar
    print("   Vectorizando textos...")
    vectorizer = CountVectorizer(
        stop_words="english",
        lowercase=True,
        max_df=max_df,
        min_df=min_df,
        max_features=max_features
    )
    X = vectorizer.fit_transform(texts)
    
    # Aplicar LDA
    print(f"   Entrenando modelo LDA ({max_iter} iteraciones)...")
    lda = LatentDirichletAllocation(
        n_components=n_topics,
        learning_method="batch",
        random_state=random_state,
        max_iter=max_iter
    )
    lda.fit(X)
    
    # Extraer palabras principales de cada tópico
    terms = vectorizer.get_feature_names_out()
    topics = []
    
    for i, component in enumerate(lda.components_):
        top_indices = component.argsort()[-n_top_words:][::-1]
        top_words = ", ".join(terms[j] for j in top_indices)
        topics.append(f"Tema {i+1}: {top_words}")
    
    print("   Tópicos extraídos exitosamente")
    return topics


def print_topics(topics: list):

    # Imprime los tópicos de manera formateada.
    
    print("\n" + "="*70)
    print("TEMAS DETECTADOS")
    print("="*70)
    for topic in topics:
        print(f"  • {topic}")
    print("="*70 + "\n")


def assign_topics_to_documents(df: pd.DataFrame,
                               text_column: str = "review_text",
                               n_topics: int = 8,
                               max_features: int = 6000,
                               max_df: float = 0.92,
                               min_df: int = 20) -> pd.DataFrame:
    
    # Asigna el tópico dominante a cada documento.
    
    df_out = df.copy()
    texts = df_out[text_column].fillna("").astype(str).tolist()
    
    # Vectorizar
    vectorizer = CountVectorizer(
        stop_words="english",
        lowercase=True,
        max_df=max_df,
        min_df=min_df,
        max_features=max_features
    )
    X = vectorizer.fit_transform(texts)
    
    # LDA
    lda = LatentDirichletAllocation(
        n_components=n_topics,
        learning_method="batch",
        random_state=42
    )
    doc_topic_dist = lda.fit_transform(X)
    
    # Asignar tópico dominante
    df_out['dominant_topic'] = doc_topic_dist.argmax(axis=1) + 1
    df_out['topic_probability'] = doc_topic_dist.max(axis=1)
    
    return df_out
