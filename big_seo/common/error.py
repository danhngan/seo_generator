class NotSupported(Exception):
    def __init(self,message: str):
        self.message = str(message)
        super().__init__(message)
    def __str__(self) -> str:
        return "This feature not supported yet: " + self.message