from instagram_client import InstagramClient
import asyncio

async def search(query: str):
    # Create 5 dummy InstagramClient users
    users = [
        InstagramClient(username='user1', password='user1pw', email='user1@user.com', email_password='user1pw', email_host='imap.user.com'),
        InstagramClient(username='user2', password='user2pw', email='user2@user.com', email_password='user2pw', email_host='imap.user.com'),
        InstagramClient(username='user3', password='user3pw', email='user3@user.com', email_password='user3pw', email_host='imap.user.com'),
        InstagramClient(username='user4', password='user4pw', email='user4@user.com', email_password='user4pw', email_host='imap.user.com'),
        InstagramClient(username='user5', password='user5pw', email='user5@user.com', email_password='user5pw', email_host='imap.user.com'),
    ]

    # Use asyncio.gather to run searches concurrently
    results = await asyncio.gather(*(user.search(query) for user in users))

    # Print results from all users
    for i, result in enumerate(results, start=1):
        print(f"Results from user{i}: {result}")

# Run the search function with a query
if __name__ == "__main__":
    query = "imbryantbarnes"
    loop = asyncio.get_event_loop()
    loop.run_until_complete(search(query))