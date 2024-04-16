import numpy as np

class ComparisonMetrics:
    _metricsList = ["euclidean", "manhattan", "cosine", "correlation", "mse", "rmse"]
    @staticmethod
    def compare_arrays(a, b, method):
        if a.shape != b.shape:
            raise ValueError("Arrays have different shapes")
        if method == "euclidean":
            return np.sqrt(np.sum((a - b) ** 2))
        elif method == "manhattan":
            return np.sum(np.abs(a - b))
        elif method == "cosine":
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        elif method == "correlation":
            return np.corrcoef(a, b)[0, 1]
        elif method == "mse":
            return np.mean((a - b) ** 2)
        elif method == "rmse":
            return np.sqrt(np.mean((a - b) ** 2))
        else:
            raise ValueError("Invalid comparison method")

    @staticmethod
    def getMetricsList():
        return ComparisonMetrics._metricsList