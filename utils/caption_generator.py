import random
import re

def generate_product_hashtags(details, max_hashtags=5):
    """Generate product-specific hashtags from title and description."""
    title = details.get("title", "")
    description = details.get("description", "")
    
    text = f"{title} {description}".lower()
    
    # Remove punctuation and split into words
    words = re.findall(r'\b\w+\b', text)
    
    # Common stop words to ignore
    stop_words = set([
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their', 'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now', 'here', 'there', 'then', 'once', 'from', 'up', 'down', 'out', 'over', 'under', 'again', 'further', 'then', 'once'
    ])
    
    # Filter words: length > 2, not stop words, not numbers
    keywords = [word for word in words if len(word) > 2 and word not in stop_words and not word.isdigit()]
    
    # Count frequency
    from collections import Counter
    word_counts = Counter(keywords)
    
    # Get most common keywords
    common_keywords = [word for word, count in word_counts.most_common(20) if count > 1 or random.random() < 0.3]  # Include some single occurrences
    
    # Create hashtags
    hashtags = [f"#{word.capitalize()}" for word in common_keywords[:max_hashtags]]
    
    return " ".join(hashtags)

def generate_caption(details, short_link):

    title = details.get("title")
    price = details.get("price")
    description = details.get("description")

    caption = ""

    if title:
        caption += f"🔥 {title}\n\n"

    if price:
        caption += f"💰 Price: {price}\n\n"

    if description:
        caption += f"{description[:200]}...\n\n"

    caption += f"🛒 Buy here:\n{short_link}\n\n"

    # Add product-specific hashtags
    product_hashtags = generate_product_hashtags(details)
    caption += f"{product_hashtags} #amazonfinds #amazondeals #onlineshopping #dealoftheday #techdeals"

    return caption