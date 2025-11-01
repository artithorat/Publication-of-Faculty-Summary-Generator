from scholarly import scholarly

# Search for "Dr. Darshan Ruikar"
search_query = scholarly.search_author('Dr. Darshan Ruikar')
author = next(search_query, None)

if author:
    print(f"Found author: {author}")
    author_details = scholarly.fill(author)
    print(f"Author details: {author_details}")
else:
    print("No author found.")
