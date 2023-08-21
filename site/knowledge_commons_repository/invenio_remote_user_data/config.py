from kombu import Exchange

REMOTE_USER_DATA_API_ENDPOINTS = {
    "knowledgeCommons": {
        "groups": {
            "remote_endpoint": "https://hcommons-staging.org",
            "remote_identifier": "id",
            "remote_method": "GET",
            "token_env_variable_label": "COMMONS_API_TOKEN",
        }
    }
}

REMOTE_USER_DATA_UPDATE_PERIOD = 60 # 1 hour

REMOTE_USER_DATA_MQ_EXCHANGE = Exchange(
    "user-data-updates",
    type="direct",
    delivery_mode="transient",  # in-memory queue
)