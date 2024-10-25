# - bookID: Unique identification number fro each book
# - title: Name under which book was published
# - authors: Name of the Authors of the book
# - average_rating: Avarage rating of the book recevied in total.
# - isbn: International standarded book number
# - isbn13: 13 digit isbn to identify the book
# - language_code: Primary Language of the book
# - num_pages: Number of pages the book containes
# - ratings_count: Total Number of ratings the book recevied.
# - text_reviews_count: Total number of written reviews recevied.
# - publication_date: Date when the book was first published
# - publisher: Name of the Pulishers



import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import seaborn as sns




df = pd.read_csv(r"dataset/books.csv", on_bad_lines = 'skip')




df.drop(['bookID', 'isbn', 'isbn13'], axis = 1, inplace = True)



df['year'] = df['publication_date'].str.split('/')
df['year'] = df['year'].apply(lambda x: x[2])




df['year'] = df['year'].astype('int')




df['year'].min()



df['year'].max()


df.to_csv(r'dataset/cleaned_data.csv',index=False)

df=pd.read_csv(r'dataset/cleaned_data.csv')

df[df['year'] == 2020][['title', 'authors','average_rating','language_code','publisher' ]]




df.groupby(['year'])['title'].agg('count').sort_values(ascending = False).head(20)





df.groupby(['language_code'])[['average_rating', 
                               'ratings_count', 
                               'text_reviews_count']].agg('mean').style.background_gradient(cmap = 'Wistia')


df[df.average_rating == df.average_rating.max()][['title','authors','language_code','publisher']]




publisher = df['publisher'].value_counts()[:20]
publisher






df.head(5)



def num_to_obj(x):
    if x >0 and x <=1:
        return "between 0 and 1"
    if x > 1 and x <= 2:
        return "between 1 and 2"
    if x > 2 and x <=3:
        return "between 2 and 3"
    if x >3 and x<=4:
        return "between 3 and 4"
    if x >4 and x<=5:
        return "between 4 and 5"
df['rating_obj'] = df['average_rating'].apply(num_to_obj)



rating_df = pd.get_dummies(df['rating_obj'])     #one hot encoding
rating_df.head()



language_df = pd.get_dummies(df['language_code'])
language_df.head()




features = pd.concat([rating_df,language_df, df['average_rating'],
                    df['ratings_count'], df['title']], axis = 1)
features.set_index('title', inplace= True)
features.head()





from sklearn.preprocessing import StandardScaler



scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)




features_scaled


# # Model Building


from sklearn import neighbors





model = neighbors.NearestNeighbors(n_neighbors=10, algorithm = 'ball_tree',
                                  metric = 'euclidean')
model.fit(features_scaled)
dist, idlist = model.kneighbors(features_scaled)



def normalize_title(title):
    """ Normalize title by removing unwanted characters and converting to lowercase. """
    return re.sub(r'[^\w\s#()]', '', title).lower().strip()

def BookRecommender(book_name):
    book_list_info = []
    
    # Normalize input
    normalized_input = normalize_title(book_name)
    
    # Normalize dataset titles for comparison
    df['normalized_title'] = df['title'].apply(normalize_title)
    
    # Check if the input contains special characters
    if re.search(r'[^\w\s]', book_name):  # Check for any non-word character
        # Logic for inputs with symbols
        print("Input contains special characters.")
        # book_id_row = df[df['normalized_title'].str.extract(re.escape(normalized_input), na=False, case=False)]
        book_id_row = df[df['normalized_title'].str.extract(normalized_input)]
        
        # You can implement specific logic here for inputs with symbols if needed
        
    else:
        # Logic for simple string inputs
        print("Input is a simple string.")
        book_id_row = df[df['normalized_title'].str.contains(re.escape(normalized_input), na=False, case=False)]
        
        # You can implement specific logic here for simple strings if needed

    if not book_id_row.empty:
        book_id = book_id_row.index[0]
        
        book_list_info.append(f"{df.iloc[book_id].title} by {df.iloc[book_id].authors}")
        
        # Assuming idlist is defined elsewhere in your code
        for newid in idlist[book_id]:
            if newid != book_id:
                recommended_title = df.iloc[newid].title
                recommended_author = df.iloc[newid].authors
                book_list_info.append(f"{recommended_title} by {recommended_author}")
                
    else:
        print(f"Book '{book_name}' not found in the database.")
    
    return book_list_info



def recommend_by_rating(min_rating):
    filtered_books = df[df['average_rating'] >= min_rating]
    
    top_books = filtered_books.sort_values(by='average_rating', ascending=False).head(125)  # Get top 125 books
    
    book_list_info = [f"{row['title']} by {row['authors']}" for index, row in top_books.iterrows()]
    
    return book_list_info


def recommend_by_publisher(publisher_name):
    filtered_books = df[df['publisher'].str.lower() == publisher_name.lower()]
    
    top_books = filtered_books.sort_values(by='average_rating', ascending=False).head(30)  #get top 25 books
    
    book_list_info = [f"{row['title']} by {row['authors']}" for index, row in top_books.iterrows()]
    
    return book_list_info
