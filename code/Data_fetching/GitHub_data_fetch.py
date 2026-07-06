import requests
import time
import csv
from urllib.parse import urlparse, parse_qs
import os
import datetime
import numpy as np

# GitHub token to bypass GitHub's 1000-record cap per search
GITHUB_TOKEN = 'Your Token'

# If the environment variable is not set, stop the script.
if not GITHUB_TOKEN:
    raise ValueError("GitHub token not found. Please set the 'GITHUB_TOKEN' environment variable.")

# DUAL HEADERS FOR REST AND GRAPHQL
graphql_headers = {"Authorization": f"bearer {GITHUB_TOKEN}"}
rest_headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}


csv_file = 'github_individuals_3000_4.csv'
fieldnames = [
    'full_repository_name', 'repository', 'owner', 'email', 'description', 
    'pull_requests', 'stars', 'forks', 'commits', 'total_public_repos', 'language',
    'total_pr_merged', 'total_issues_opened', 'total_issues_closed', 
    'total_commits_last_year', 'total_commits_all_time', 'avg_commits_per_month',
    'avg_issue_close_time', 'latest_commit_message'
]

# THE GRAPHQL QUERY
GRAPHQL_QUERY = """
query ownerDetails($owner: String!) {
  user(login: $owner) {
    publicRepositories: repositories(first: 1) {
      totalCount
    }
    openedIssues: issues {
      totalCount
    }
    closedIssues: issues(states: CLOSED) {
      totalCount
    }
  }
}
"""


# Define time windows to bypass GitHub's 1000-record cap per search
date_ranges = [
    ('2020-01-01', '2020-06-30'),
    ('2020-07-01', '2020-12-31'),
    ('2019-01-01', '2019-06-30'),
    ('2019-09-01', '2019-12-31')
]

def get_total_count_from_link_header(response):
   
    link_header = response.headers.get('Link')
    if not link_header:
        return len(response.json())

    last_link = [link for link in link_header.split(',') if 'rel="last"' in link]
    if not last_link:
        return len(response.json())
        
    try:
        last_url = last_link[0].split(';')[0].strip().strip('<>')
        parsed_url = urlparse(last_url)
        query_params = parse_qs(parsed_url.query)
        return int(query_params.get('page', [1])[0])
    except (IndexError, ValueError) as e:
        print(f"Could not parse last page number from link: {last_link}. Error: {e}")
        return len(response.json())

def get_owner_graphql_data(owner):
   
    try:
        variables = {"owner": owner}
        response = requests.post(
            "https://api.github.com/graphql",
            json={'query': GRAPHQL_QUERY, 'variables': variables},
            headers=graphql_headers
        )
        response.raise_for_status()
        data = response.json().get('data', {})
        if data and data.get('user'):
            return data['user']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching GraphQL data for {owner}: {e}")
    return {}


with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    total_repos_saved = 0
    processed_repos = set()

    for start_date, end_date in date_ranges:
        if total_repos_saved >= 3000:
            break
            
        for page in range(1, 11):
            if total_repos_saved >= 3000:
                break

            print(f"Fetching page {page} for repositories created between {start_date} and {end_date}...")
            # --- CHANGE: Added language:python to the search query ---
            params = {
                'q': f'stars:>10 language:python created:{start_date}..{end_date}',
                'sort': 'stars',
                'order': 'desc',
                'per_page': 100,
                'page': page
            }

            try:
                response = requests.get('https://api.github.com/search/repositories', headers=rest_headers, params=params)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error fetching repositories: {e}")
                time.sleep(60)
                continue

            repositories = response.json().get('items', [])
            if not repositories:
                break

            for repo in repositories:
                if total_repos_saved >= 3000:
                    break

                full_name = repo['full_name']
                
                if full_name in processed_repos:
                    continue

                if repo['owner']['type'] != 'User':
                    continue

                #  Extracting core data
                owner, repository_name = full_name.split('/')
                description = repo.get('description', 'N/A')
                stars = repo['stargazers_count']
                forks = repo['forks_count']
                language = repo.get('language', 'N/A')
                repo_created_at = repo.get('created_at')

                # CHANGE: Fetch owner data with GraphQL
                owner_data = get_owner_graphql_data(owner)
                if not owner_data:
                    continue
                
                # Initialize all variables 
                pull_requests = 0
                email = 'N/A'
                total_public_repos = 'N/A'
                total_pr_merged = 0
                total_issues_opened = 0
                total_issues_closed = 0
                total_commits_last_year = 0
                total_commits_all_time = 0
                avg_commits_per_month = 0
                avg_issue_close_time = 0
                latest_commit_message = 'N/A'

                
                # Get total commits
                try:
                    commits_url = repo['commits_url'].replace('{/sha}', '')
                    commits_resp = requests.get(commits_url, headers=rest_headers, params={'per_page': 1})
                    commits_resp.raise_for_status()
                    total_commits_all_time = get_total_count_from_link_header(commits_resp)
                    latest_commit = commits_resp.json()
                    if latest_commit:
                        email = latest_commit[0]['commit']['author'].get('email', 'N/A')
                        latest_commit_message = latest_commit[0]['commit'].get('message', 'N/A')
                    else:
                        email = 'N/A'

                    # Get total commits in the last year
                    last_year_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=365)
                    last_year_params = {'since': last_year_date.isoformat(), 'per_page': 1}
                    last_year_resp = requests.get(commits_url, headers=rest_headers, params=last_year_params)
                    last_year_resp.raise_for_status()
                    total_commits_last_year = get_total_count_from_link_header(last_year_resp)

                    # Calculate avg commits per month
                    if total_commits_all_time > 0 and repo_created_at:
                        created_date = datetime.datetime.strptime(repo_created_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
                        months_since_creation = (datetime.datetime.now(datetime.timezone.utc) - created_date).days / 30.44
                        if months_since_creation > 0:
                            avg_commits_per_month = total_commits_all_time / months_since_creation
                
                except requests.exceptions.RequestException:
                    email = 'N/A'
                    total_commits_all_time = 0
                    total_commits_last_year = 0
                    avg_commits_per_month = 0
                    latest_commit_message = 'N/A'

                # Get total pull requests (merged, opened, closed)
                try:
                    pr_url = repo['pulls_url'].replace('{/number}', '')
                    
                    merged_pr_resp = requests.get(pr_url, headers=rest_headers, params={'state': 'closed', 'per_page': 1})
                    merged_pr_resp.raise_for_status()
                    total_pr_merged = get_total_count_from_link_header(merged_pr_resp)

                    pr_resp = requests.get(pr_url, headers=rest_headers, params={'state': 'all', 'per_page': 1})
                    pr_resp.raise_for_status()
                    pull_requests = get_total_count_from_link_header(pr_resp)

                except requests.exceptions.RequestException:
                    pull_requests = 0
                    total_pr_merged = 0

                # Get issues data
                try:
                    issues_url = repo['issues_url'].replace('{/number}', '')
                    
                    closed_issues_resp = requests.get(issues_url, headers=rest_headers, params={'state': 'closed', 'per_page': 100})
                    closed_issues_resp.raise_for_status()
                    closed_issues_data = closed_issues_resp.json()
                    total_issues_closed = get_total_count_from_link_header(closed_issues_resp)

                    if total_issues_closed > 0:
                        close_times = []
                        for issue in closed_issues_data:
                            created_at = datetime.datetime.strptime(issue['created_at'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
                            closed_at = datetime.datetime.strptime(issue['closed_at'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
                            close_times.append((closed_at - created_at).total_seconds())
                        avg_issue_close_time = np.mean(close_times) if close_times else 0
                    else:
                        avg_issue_close_time = 0

                except requests.exceptions.RequestException:
                    total_issues_closed = 0
                    avg_issue_close_time = 0
                    
                # Get total public repositories and issue counts for the owner from GraphQL
                total_public_repos = owner_data.get('publicRepositories', {}).get('totalCount', 'N/A')
                total_issues_opened = owner_data.get('openedIssues', {}).get('totalCount', 'N/A')
                total_issues_closed = owner_data.get('closedIssues', {}).get('totalCount', 'N/A')

                # Save to CSV
                writer.writerow({
                    'full_repository_name': full_name, 'repository': repository_name, 'owner': owner,
                    'email': email, 'description': description, 'pull_requests': pull_requests,
                    'stars': stars, 'forks': forks, 'commits': total_commits_all_time,
                    'total_public_repos': total_public_repos, 'language': language,
                    'total_pr_merged': total_pr_merged, 'total_issues_opened': total_issues_opened,
                    'total_issues_closed': total_issues_closed, 'total_commits_last_year': total_commits_last_year,
                    'total_commits_all_time': total_commits_all_time,
                    'avg_commits_per_month': avg_commits_per_month,
                    'avg_issue_close_time': avg_issue_close_time,
                    'latest_commit_message': latest_commit_message
                })

                processed_repos.add(full_name)
                total_repos_saved += 1
                print(f"({total_repos_saved}/3000) Saved: {full_name} (Language: {language})")
                
                time.sleep(1)

            time.sleep(1)

print(f"\nData collection complete. Total individual user repositories collected: {total_repos_saved}")