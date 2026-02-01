from db import get_connection
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F


# Step 1: fetch news form the database

conn = get_connection()
cursor = conn.cursor()

sql_query = """
        SELECT id, title, description FROM news WHERE sentiment_label IS NULL
        """

cursor.execute(sql_query)
rows = cursor.fetchall()

# Step 2: load pre-trained model and tokenizer
model_name = "ProsusAI/finbert" 
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Step 3: perform sentiment analysis and update the database
for row in rows:
    content = f"{row[1]}. {row[2]}" # Combine title and description
    inputs = tokenizer(content, return_tensors="pt")
    labels = model.config.id2label

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = F.softmax(logits, dim=-1)
        predicted_class_id = torch.argmax(probabilities).item()
        sentiment_label = labels[predicted_class_id]
        sentiment_score = probabilities[0][predicted_class_id].item()
        