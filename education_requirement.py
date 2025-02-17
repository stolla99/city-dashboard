import pandas as pd
import plotly.graph_objects as go


def get_dataframe_employer_education():
    df_employ = pd.read_csv('resources/attributes/Jobs.csv')
    df_employloc = pd.read_csv('resources/attributes/Employers.csv')
    series1 = df_employ['employerId'].unique()
    d = {'employerId': series1}
    df_new = pd.DataFrame(data=d)
    df_lc = df_employ.loc[df_employ['educationRequirement'] == 'Low', 'employerId']
    d2 = df_lc.value_counts(sort=False)
    df_between = pd.DataFrame(data=d2)
    df_between = df_between.reset_index()
    df_between.columns = ['employerId', 'LowCount']
    df_new = df_new.merge(df_between, how='left', left_on='employerId', right_on='employerId')
    df_lc2 = df_employ.loc[df_employ['educationRequirement'] == 'HighSchoolOrCollege', 'employerId']
    d3 = df_lc2.value_counts(sort=False)
    df_between2 = pd.DataFrame(data=d3)
    df_between2 = df_between2.reset_index()
    df_between2.columns = ['employerId', 'HighSchoolOrCollegeCount']
    df_new = df_new.merge(df_between2, how='left', left_on='employerId', right_on='employerId')
    df_lc3 = df_employ.loc[df_employ['educationRequirement'] == 'Bachelors', 'employerId']
    d4 = df_lc3.value_counts(sort=False)
    df_between3 = pd.DataFrame(data=d4)
    df_between3 = df_between3.reset_index()
    df_between3.columns = ['employerId', 'BachelorsCount']
    df_new = df_new.merge(df_between3, how='left', left_on='employerId', right_on='employerId')
    df_lc4 = df_employ.loc[df_employ['educationRequirement'] == 'Graduate', 'employerId']
    d5 = df_lc4.value_counts(sort=False)
    df_between4 = pd.DataFrame(data=d5)
    df_between4 = df_between4.reset_index()
    df_between4.columns = ['employerId', 'GraduateCount']
    df_new = df_new.merge(df_between4, how='left', left_on='employerId', right_on='employerId')
    df_new = df_new.fillna(0)
    return df_new.merge(df_employloc, how='left', left_on='employerId', right_on='employerId')


fig = go.Figure([go.Bar()])
