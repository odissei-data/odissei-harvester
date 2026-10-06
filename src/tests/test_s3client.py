from S3Client import get_s3_client


def test_s3_calls_time_out():
    config = get_s3_client("http://localhost:1", "x", "y").meta.config
    assert config.connect_timeout == 5
    assert config.retries == {"mode": "standard", "total_max_attempts": 3}
