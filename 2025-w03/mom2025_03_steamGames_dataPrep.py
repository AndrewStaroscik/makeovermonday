# %%
#setup

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import json

# %%
# get data

df = pd.read_csv('https://query.data.world/s/oft5fzynb4c3osd3jsspdg2iyplqep?dws=00000')
df.head()

# %%
# get a list of the tags

df['tagList'] = df['Genre Tags'].str.split(',').apply(lambda tags: [tag.strip() for tag in tags])
uniqueTags = sorted(set(tag for tags in df['Genre Tags'] for tag in tags))

# %%
# make a binary matrix of tags for each game

tagMatrix = pd.DataFrame(
    [
        [1 if tag in tags else 0 for tag in uniqueTags]
        for tags in df['Genre Tags']
    ],
    columns=uniqueTags,
    index=df['Name']
)

# %%
# do the comparison using cosine simiarity 

similarityMatrix = cosine_similarity(tagMatrix)
similarityDf = pd.DataFrame(similarityMatrix, index=df['Name'], columns=df['Name'])

# %%
# Function to get lists of 3 most similar games for each game

def get_top_similar_games(similarity_row, game_name, top_n=3):
    sorted_similarities = similarity_row.sort_values(ascending=False)
    return sorted_similarities.drop(game_name).head(top_n).index.tolist()

# %%
# create the link and node arrays

links = []
for game in similarityDf.index:
    similar_games = get_top_similar_games(similarityDf.loc[game], game, top_n=3)
    for similar_game in similar_games:
        print(game)
        links.append({"source": game, "target": similar_game})

nodes = []

for _, r in df.iterrows():
  nodes.append({'game': r['Name'], 'popularity': r['Peak Today'], 'price': r['Price']})

# %%
# make nested json structure and export

gamesNodeTagLink_json = {
    'nodes': nodes,
    'links': links
}

# Save as JSON file
with open('gamesAsNodes.json', 'w') as f:
    json.dump(gamesNodeTagLink_json, f, indent=2)


