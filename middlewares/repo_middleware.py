from aiogram import BaseMiddleware

class RepoMiddleware(BaseMiddleware):
    def __init__(self, repo):
        self.repo = repo
    
    async def __call__(self, handler, event, data):
        data["repo"] = self.repo
        # подложить repo в data
        # вызвать хендлер
        return await handler(event, data)