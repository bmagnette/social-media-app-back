import logging
import os
from functools import partial

import requests
from flask import Blueprint

from core.helpers.handlers import response_wrapper, login_required
from core.models.user import User

logger = logging.getLogger(__name__)

unsplash = Blueprint('unsplash', __name__)

BASE_URL = 'https://api.unsplash.com'


@unsplash.route("/unsplash/<query>", methods=["GET"])
@partial(login_required)
def query_unsplash_photo(current_user: User, query: str):
    params = {
        "query": query,
        "page": 1,
        "per_page": 21,
        "order_by": "relevant",
        "orientation": "squarish"
    }

    response = requests.get(BASE_URL + f"/search/photos?client_id={os.environ['UNSPLASH_ACCESS_TOKEN']}", params=params)
    response.raise_for_status()
    return response_wrapper("content", response.json()["results"], 200)
