import pandas as pd
import plotly.express as px

df_age = pd.read_csv("resources/attributes/Participants.csv")
l = list(set(df_age['age']))
df_age_list = list(df_age['age'])
l.sort()
lab = ['18-22', '23-27', '28-32', '33-37', '38-42', '43-47', '48-52', '53-57', '57-61']
res = [0] * 9

df_degree = pd.read_csv('resources/attributes/Participants.csv')
series = df_degree['educationLevel'].value_counts()

df_result = pd.DataFrame(series)
df_result = df_result.reset_index()
df_result.columns = ['education', 'total']
fig = px.pie(df_result, values='total', names='education')
fig.show()
