"""共用應用程式設定。"""


class Config:
    DEBUG = False
    TESTING = False
    MAX_UPLOAD_BYTES = 100 * 1024
    MAX_CONTENT_LENGTH = MAX_UPLOAD_BYTES + 64 * 1024
    ALLOWED_EXTENSIONS = ("pdf", "docx", "zip", "txt")
