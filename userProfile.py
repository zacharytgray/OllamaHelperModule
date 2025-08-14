import json

class User:
    def __init__(self, profilePath: str):
        self.profileFilePath = profilePath
        self.profile = {}
        self.loadProfile()

    def addToProfile(self, key: str, value: str):
        self.profile[key] = value

    def getProfile(self):
        return self.profile

    def clearProfile(self):
        self.profile.clear()

    def saveProfile(self):
        with open(self.profileFilePath, 'w') as f:
            json.dump(self.profile, f, indent=4)

    def loadProfile(self):
        try:
            with open(self.profileFilePath, 'r') as f:
                self.profile = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.profile = {}

    def toString(self):
        if not isinstance(self.profile, dict):
            return "(No profile loaded)"
        return "\n".join([f"{key}: {value}" for key, value in self.profile.items()])