import pandas as pd
import geopy.distance
from keras.models import load_model
import tokanizer_and_cleaner
import numpy as np

def get_lstm_prediction(description):
    # Step 1: Load the user_book.csv dataset
    df = pd.read_csv('E:\\RESEARCH\\rec\\bookgramb\\data\\books_with_users.csv')

    # Step 2: Load the saved LSTM model
    model = load_model('E:\\RESEARCH\\rec\\bookgramb\\models\\BookModel2.h5')

    # Step 3: Preprocess the text data in the description column of the df dataframe
    max_desc_length=200

    labels = ['fiction', 'nonfiction']
    cleaned_text = tokanizer_and_cleaner.clean_text(description)
    tokenized_text = tokanizer_and_cleaner.tokenizer(cleaned_text, tokanizer_and_cleaner.vocab_dict, max_desc_length)
    input_data = np.reshape(tokenized_text, (1, max_desc_length))
    # Step 4: Use the loaded LSTM model to predict the genre of books
    output = model.predict(input_data, batch_size=1)
    score = (output > 0.5) * 1
    pred = score.item()


    # Step 5: Compare the predicted genre with the actual genre in the label column of the df dataframe
    df['predicted_genre'] = labels[pred]

    # Step 6: Filter the top 10 books with the predicted genre
    top_books = df[df['predicted_genre'] == df['label']].head(30)

    # Step 7: Print the top 10 books with the predicted genre
    print(top_books)
    return top_books

# Define the rule-based recommendation function
def rule_based_recommendation(top10_books, occupied):
    if occupied == 1:
        # If the user is currently occupying a location, recommend books with high ratings
        recommendations = top10_books[top10_books['book_rating'] >= 4.0].sort_values(by=['book_rating'], ascending=False)
    else:
        # If the user is not currently occupying a location, recommend popular books
        recommendations = top10_books.sort_values(by=['book_rating_count', 'book_review_count'], ascending=False)

    # Return the top 10 recommendations
    return recommendations.head(30)

# Define the geographical recommendation function
def geographical_recommendation(top10_books, location):
    # Extract the latitude and longitude values from the location string
    top10_books['latitude'] = top10_books['location'].apply(lambda x: float(x.strip('[]').split(',')[0]))
    top10_books['longitude'] = top10_books['location'].apply(lambda x: float(x.strip('[]').split(',')[1]))

    # Compute the distance between each user and the target location
    top10_books['distance'] = top10_books.apply(lambda row: geopy.distance.distance((row['latitude'], row['longitude']), location).km, axis=1)
    # Sort the books by distance
    recommendations = top10_books.sort_values(by=['distance'])
    # print(recommendations)
    # Return the top 10 recommendations
    return recommendations.head(30)

# Define the hybrid recommendation function
def hybrid_recommendation(top10_books, occupied, location):
    # Get the recommendations from the rule-based and geographical recommendation systems
    rule_based_recommendations = rule_based_recommendation(top10_books, occupied)
    geographical_recommendations = geographical_recommendation(rule_based_recommendations, location)

    # Combine the two sets of recommendations and remove duplicates
    recommendations = pd.concat([rule_based_recommendations, geographical_recommendations])
    recommendations = recommendations.drop_duplicates(subset='book_id')

    # Return the top 10 recommendations
    return recommendations.head(30)

