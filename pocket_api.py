import json

import pocket


class PocketWrapper:

    def __init__(self, consumer_key, redirect_uri):
        self.consumer_key = consumer_key
        self.redirect_uri = redirect_uri

    def authenticate_start(self):
        try:
            request_token = pocket.Pocket.get_request_token(
                consumer_key=self.consumer_key, redirect_uri=self.redirect_uri
            )
            return request_token
        except Exception as e:
            raise Exception(f"Error getting request token: {e}")

    def get_auth_url(self, request_token):
        return pocket.Pocket.get_auth_url(
            code=request_token, redirect_uri=self.redirect_uri
        )

    def authenticate_complete(self, request_token):
        try:
            user_credentials = pocket.Pocket.get_credentials(
                consumer_key=self.consumer_key, code=request_token
            )
            return user_credentials["access_token"]
        except Exception as e:
            raise Exception(f"Error getting access token: {e}")

    def save_access_token(self, token):
        with open("access_token.json", "w") as f:
            json.dump({"access_token": token}, f)

    def load_access_token(self):
        try:
            with open("access_token.json", "r") as f:
                data = json.load(f)
                return data.get("access_token")
        except FileNotFoundError:
            return None

    def get_articles(self, access_token):
        if not access_token:
            raise Exception("You must authenticate first.")

        # Step 4: Create a Pocket instance and get articles
        try:
            pocket_instance = pocket.Pocket(self.consumer_key, access_token)
            response = pocket_instance.get()
            return response
        except Exception as e:
            print(f"Error getting articles: {e}")
            raise
