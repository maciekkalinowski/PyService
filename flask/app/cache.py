


class PyServiceCache():
    testCache = ["a", "b", "c"]
    testValue = "BAC"

    usersCache = []
    
    def getUsersCache(self):
        return self.usersCache
    
    def refreshUsersCache(self):
        self.usersCache = [('user1', 'user1'), ('user2', 'user2'), ('user3', 'user3')]
        return self.usersCache


    def getTestCache(self):
        return self.testCache

    def addToTestCache(self, newValue):
        self.testCache.append(newValue)
        return self.getTestCache