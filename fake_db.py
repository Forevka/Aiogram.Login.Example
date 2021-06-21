class FakeRepo():
    def get_user(self, user_id: int):
        return  {
            "user_id": user_id,
            "role_id": 1,
        }
