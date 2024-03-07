import jwt


def make_token(user_info_dict: dict) -> str:
    token = jwt.encode(
        user_info_dict,
        key="secret",
    )
    return token


if __name__ == "__main__":
    print(
        make_token(
            user_info_dict={
                "id": 123,
                "name": "Tom Bar",
            }
        )
    )
