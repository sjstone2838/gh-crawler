Github Crawler
=======================================

This repository supports the collection and organization of activity data on Github users,
for the purpose of statistical analysis (prediction of "successful" users based on activity in 
months 1-12 after joining.) Success could be defined based on number of repos, number of non-fork
repos, forks, forks/repo, stars, stars/repo, followers, or a combination of the above.

This project relies on the Github API and GithubArchive via the Google BigQuery AI, and requires
authentication credentials for both, saved as local environment variables.


SETUP
---------------

Clone the repository
```sh
git clone https://github.com/sjstone/gh-crawler.git
```

```sh
cd gh-crawler
```
Make sure you are working in a virtualenv, then run:
```sh
pip install requirements
```

Ensure that the following are all set as local environment variables. You will need to get Google
BigQuery credentials if you do not already have them:
```sh
SECRET_KEY = get_env_variable('GH_CRAWLER_DJANGO_SECRET_KEY')
GITHUB_CLIENT_ID = get_env_variable('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = get_env_variable('GITHUB_CLIENT_SECRET')
```

Set up a local Django database:
```sh
python manage.py makemigrations
```
then, 
```sh
python manage.py migrate
```

```sh
python manage.py createsuperuser
```

COLLECTING AND ORGANIZING GITHUB USER DATA
---------------
First, collect high-level Github user data on a set of users, starting with a Github user id 
and a the number of users on which data is to be collect (the limit):
```sh
python manage.py crawl_devs_by_id [starting_id] [limit]
```

For each user, append additional data to Developer object by making a user profile call to Github API
Can be executed on multiple user groups simultaneously with different pk ranges.
```sh
python manage.py append_profiles_by_id_range [gh_id_min] [gh_id_max]
```

Query BigQuery dataset at [dateset_name] for all events where where actor is in 
the range where user's primary key is between [pk_min - pk_max]. Note that BigQuery makes available
Github public events via GithubArchive in daily, monthly, and yearly files. 
Example dataset_name: githubarchive_2011.2014_copy
```sh
python manage.py get_events_by_actor [dataset_name] [pk_min] [pk_max]
```

Query Github API for repo details that are not included in user profile. This appends data such as
non-fork repos, fork count per repo, and star count per repo. 
Can be executed on multiple user groups simultaneously with different pk ranges.
```sh
python manage.py get_repos_by_developer [pk_min] [pk_max]
```

Update or create repo statistics (original / non-fork repos, fork count, forks/repo, 
star count, stars/repo) on Developer objects. These statistics, in addition to follower 
count, are possible response variables for statistical analysis.
Note that repos may have been deleted, so Developer.public_repos may exceed the count of 
Repos with detailed data from API calls.
Can be executed on multiple user groups simultaneously with different pk ranges.
```sh
python manage.py write_repo_statistics [pk_min] [pk_max]
```

Update or create TemporalPredictors for users in pk range. These are the features for 
statistical learning. TemporalPredictors are the count by event type by month by user. 
So each user will have temporal predictors ForkEvent_Count_09_2014, PushEvent_Count_09_2014, etc. 
In addition to the standard events logged in the GitHub public timeline,
this will classify Pull Requests into Quality Opened PRs (where the PR
was merged by someone else) and Quality Closed PRs (where the actor
closed a PR opened by someone else) - these indicate collaborative work.
Can be executed on multiple user groups simultaneously with different pk ranges.
```sh
python manage.py write_temporal_predictors [pk_min] [pk_max]
```

There is no command (yet) for condensing all the features and possible responses to a flat file
for all users. However, the following command can be used to write the features and response for
one user to CSV for visualization purposes.  

Write information on dev in range to a flat file, with features arrayed as
a matrix (months on x-axis, event-type on y-axis).
Response variables are included in cell with Dev's login.
```sh
python manage.py summarize_by_dev [dev_login]
```

