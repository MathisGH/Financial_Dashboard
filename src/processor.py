from src.db import get_connection
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F


model_name = "ProsusAI/finbert" 
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

def process_sentiments():
    conn = get_connection()
    cursor = conn.cursor()

    sql_query = """
            SELECT id, title, description FROM news WHERE sentiment_label IS NULL
            """

    cursor.execute(sql_query)
    rows = cursor.fetchall()
    if not rows:
        print("No new articles to process.")
        return 

    print(f"Processing {len(rows)} articles...")

    data_to_update = []
    for row in rows:
        title = row[1]
        description = row[2] if row[2] else ""
        content = f"{title}. {description}" # Combine title and description
        inputs = tokenizer(content, return_tensors="pt", truncation=True, max_length=512, padding=True) # Truncate long texts, set max length because of model limits and padding is needed for batch processing (even if single input, puts "" tokens to make up length)
        labels = model.config.id2label

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probabilities = F.softmax(logits, dim=-1)
            predicted_class_id = torch.argmax(probabilities).item()
            sentiment_label = labels[predicted_class_id]
            sentiment_score = probabilities[0][predicted_class_id].item()
            data_to_update.append((sentiment_label, sentiment_score, row[0]))

    if data_to_update:
        update_query = """
            UPDATE news
            SET sentiment_label = ?, sentiment_score = ?
            WHERE id = ?
            """
        cursor.executemany(update_query, data_to_update)
        conn.commit()
        print(f"Successfully updated {len(data_to_update)} articles.")

    conn.close()

### -------------------------------------------------------------------------------------------------------------- ###

if __name__ == "__main__":
    process_sentiments()