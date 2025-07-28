import os
import dotenv

class SecretsLoader:
    """Contains helper methods to retrieve local secrets."""

    @staticmethod
    def get_token(token_name :str, token_path :str=".env") -> str:
        """Retrieves a token either locally or remotely (if not local).

        Args:
            token_name (str): name of the token to retrieve
            token_path (str): path to the token (.env) file if needed (default is '.env')

        Returns:
            str: the token retrieved
        """
        if dotenv.load_dotenv(token_path):
            print(f"\tLoaded {token_name} from token file: {token_path}")
        else:
            raise FileNotFoundError(
                f"Could not load token: {token_name}, check if token exists in given token file."
            )

        if (os.environ.get(token_name)):
            return str(os.getenv(token_name))
        else:
            raise OSError(
                f"Could not retrieve token: {token_name}. Ensure it is defined in your environment."
            ) 