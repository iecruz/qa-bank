class Config(object):
    DEBUG=True
    SECRET_KEY='>\x1a9\xbbJ>\xf7\xb61\xec\xb95\xc2\xc8s\xe4!)\x0e\xa8^\xb5\xc5+'

class ProductionConfig(Config):
    DEBUG=False

class DevelopmentConfig(Config):
    DEBUG=True