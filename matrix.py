# Import libraries
import numpy as np
import pandas as pd

# Reading ratings file
ratings = pd.read_csv('dataset/ratings.csv', encoding='latin-1', usecols=['userId', 'movieId', 'rating', 'timestamp'])

# Reading users file
#users = pd.read_csv('dataset/users.csv', encoding='latin-1', usecols=['user_id', 'gender', 'zipcode', 'age_desc', 'occ_desc'])

# Reading movies file
movies = pd.read_csv('dataset/movies.csv', encoding='latin-1', usecols=['movieId', 'title', 'genres'])

movies.head()

ratings.head()

n_users = ratings.userId.unique().shape[0]
n_movies = ratings.movieId.unique().shape[0]


Ratings = ratings.pivot(index = 'userId', columns ='movieId', values = 'rating').fillna(0)
Ratings.head()

R = Ratings.as_matrix()
user_ratings_mean = np.mean(R, axis = 1)
Ratings_demeaned = R - user_ratings_mean.reshape(-1, 1)


sparsity = round(1.0 - len(ratings) / float(n_users * n_movies), 3)
#print 'The sparsity level of MovieLens1M dataset is ' +  str(sparsity * 100) + '%'

from scipy.sparse.linalg import svds
U, sigma, Vt = svds(Ratings_demeaned, k = 50)

sigma = np.diag(sigma)

all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_ratings_mean.reshape(-1, 1)
preds = pd.DataFrame(all_user_predicted_ratings, columns = Ratings.columns)


def recommend_movies(predictions, userID, movies, original_ratings, num_recommendations):
    
    # Get and sort the user's predictions
    user_row_number = userID - 1 # User ID starts at 1, not 0
    sorted_user_predictions = preds.iloc[user_row_number].sort_values(ascending=False) # User ID starts at 1
    
    # Get the user's data and merge in the movie information.
    user_data = original_ratings[original_ratings.userId == (userID)]
    user_full = (user_data.merge(movies, how = 'left', left_on = 'movieId', right_on = 'movieId').
                     sort_values(['rating'], ascending=False)
                 )

   # print 'User {0} has already rated {1} movies.'.format(userID, user_full.shape[0])
   # print 'Recommending highest {0} predicted ratings movies not already rated.'.format(num_recommendations)
    
    # Recommend the highest predicted rating movies that the user hasn't seen yet.
    recommendations = (movies[~movies['movieId'].isin(user_full['movieId'])].
         merge(pd.DataFrame(sorted_user_predictions).reset_index(), how = 'left',
               left_on = 'movieId',
               right_on = 'movieId').
         rename(columns = {user_row_number: 'Predictions'}).
         sort_values('Predictions', ascending = False).
                       iloc[:num_recommendations, :-1]
                      )

    return user_full, recommendations


already_rated, predictions = recommend_movies(preds, 50, movies, ratings, 20)

already_rated.head(20)

predictions
