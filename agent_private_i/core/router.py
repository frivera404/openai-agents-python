class Router:
    def __init__(self, workers: dict):
        self.workers = workers

    def pick(self, assigned_role: str):
        if assigned_role not in self.workers:
            raise ValueError(f"No worker registered for role: {assigned_role}")
        return self.workers[assigned_role]
