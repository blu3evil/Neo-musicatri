from utils.context import ResourceContext

class ClientContext(ResourceContext):
    def __init__(self):
        ResourceContext.__init__(self, client)