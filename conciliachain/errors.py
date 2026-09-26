class ConciliaChainError(Exception): pass
class ValidationError(ConciliaChainError): pass
class StorageError(ConciliaChainError): pass
class SealError(ConciliaChainError): pass
