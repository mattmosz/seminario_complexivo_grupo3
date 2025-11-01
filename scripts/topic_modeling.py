import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation


def get_extended_stop_words():
    """
    Obtiene una lista extendida de stop words combinando sklearn y nltk.
    """
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    
    # Lista base de sklearn
    stop_words = set(ENGLISH_STOP_WORDS)
    
    # Intentar agregar stop words de NLTK
    try:
        import nltk
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
        
        from nltk.corpus import stopwords
        nltk_stops = set(stopwords.words('english'))
        stop_words.update(nltk_stops)
    except:
        pass  # Si falla, solo usar sklearn
    
    # Agregar palabras adicionales comunes en reseñas de hoteles
    custom_stops = {
        'hotel', 'room', 'stay', 'stayed', 'night', 'nights',
        'booking', 'booked', 'book', 'reservation', 'reserved',
        'staff', 'service', 'location', 'place', 'time',
        'good', 'great', 'nice', 'bad', 'terrible',
        'like', 'really', 'just', 'got', 'went', 'come', 'came',
        'would', 'could', 'should', 'also', 'well', 'even',
        'however', 'although', 'though', 'still', 'yet',
        'positive', 'negative', 'review', 'reviews',
        'said', 'told', 'asked', 'did', 'does', 'done',
        'thing', 'things', 'way', 'ways', 'day', 'days',
        'bit', 'lot', 'lots', 'much', 'many', 'very', 'quite',
        'nbsp'  # Artefacto HTML común
    }
    stop_words.update(custom_stops)
    
    return list(stop_words)


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
    
    # Obtener stop words extendidas
    extended_stops = get_extended_stop_words()
    
    # Vectorizar
    print("   Vectorizando textos...")
    print(f"   Usando {len(extended_stops)} stop words...")
    vectorizer = CountVectorizer(
        stop_words=extended_stops,
        lowercase=True,
        max_df=max_df,
        min_df=min_df,
        max_features=max_features,
        token_pattern=r'\b[a-z]{3,}\b'  # Solo palabras de 3+ letras
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
    
    # Obtener stop words extendidas
    extended_stops = get_extended_stop_words()
    
    # Vectorizar
    vectorizer = CountVectorizer(
        stop_words=extended_stops,
        lowercase=True,
        max_df=max_df,
        min_df=min_df,
        max_features=max_features,
        token_pattern=r'\b[a-z]{3,}\b'  # Solo palabras de 3+ letras
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
