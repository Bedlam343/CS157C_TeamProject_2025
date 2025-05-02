# File contains code that was used to parse the raw data into csv files
import pandas as pd
import pickle
import random
import string

# convert the data into a csv file
def to_csv():

  dataset_directory = "LinkedIn_Dataset.pcl"
  with open(dataset_directory, "rb") as f:
      data = pickle.load(f)

  df = pd.DataFrame(data)

  intro_df = df['Intro'].apply(pd.Series)

  # Filter out rows where Location, Photo, or Followers are NaN
  filtered_df = intro_df.dropna(subset=['Location', 'Photo', 'Followers'])

  fields_to_keep = ['Full Name', 'Workplace', 'Location', 'Photo', 'Followers']

  filtered_df = filtered_df[fields_to_keep]
  filtered_df['name'] = df['Full Name']
  filtered_df["id"] = filtered_df.index

  final_df = filtered_df[['id', 'name', 'Workplace', 'Location', 'Photo', 'Followers']]
  final_df.rename(columns={
      'Workplace': 'bio',
      'Location': 'location',
      'Photo': 'photo',
      'Followers': 'followers',
  }, inplace=True)

  final_df.to_csv("profiles.csv", index=False)

# create random 3-6 connections for each profile
def create_connections():
  df = pd.read_csv("profiles.csv")

  user_ids = df['id'].tolist()
  edges = set()

  for user in user_ids:
      possible_targets = [uid for uid in user_ids if uid != user]
      targets = random.sample(possible_targets, k=random.randint(3,6))

      for target in targets:
          edge = tuple(sorted((user, target)))
          edges.add(edge)

  edges_df = pd.DataFrame(list(edges), columns=["source", "target"])
  edges_df.to_csv("edges.csv", index=False)

# add email, password, and username field to each profile
def generate_auth():
  df = pd.read_csv("profiles_without_auth.csv")

  def generate_username(name):
      parts = name.lower().split()
      base = ''.join(parts)
      suffix = str(random.randint(1,999))
      return base + suffix

  def generate_email(username):
      return f"{username}@gmail.com"

  def generate_password(length=8):
      return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

  df['username'] = df['name'].apply(generate_username)
  df['email'] = df['username'].apply(generate_email)
  df['password'] = df['username'].apply(lambda _: generate_password())

  df.to_csv("profiles.csv", index=False)