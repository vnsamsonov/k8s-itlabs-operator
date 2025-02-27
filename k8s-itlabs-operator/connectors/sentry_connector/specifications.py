SENTRY_APP_NAME_LABEL = "app"

SENTRY_CONNECTOR_REQUIRED_LABELS = (
    SENTRY_APP_NAME_LABEL,
)

SENTRY_INSTANCE_NAME_ANNOTATION = "sentry.connector.itlabs.io/instance-name"
SENTRY_ENVIRONMENT_ANNOTATION = "sentry.connector.itlabs.io/environment"
SENTRY_VAULT_PATH_ANNOTATION = "sentry.connector.itlabs.io/vault-path"
SENTRY_PROJECT_ANNOTATION = "sentry.connector.itlabs.io/project"
SENTRY_TEAM_ANNOTATION = "sentry.connector.itlabs.io/team"

SENTRY_CONNECTOR_REQUIRED_ANNOTATIONS = (
    SENTRY_INSTANCE_NAME_ANNOTATION,
    SENTRY_VAULT_PATH_ANNOTATION,
)

SENTRY_CONNECTOR_ANNOTATIONS = (
    SENTRY_INSTANCE_NAME_ANNOTATION,
    SENTRY_ENVIRONMENT_ANNOTATION,
    SENTRY_VAULT_PATH_ANNOTATION,
    SENTRY_PROJECT_ANNOTATION,
    SENTRY_TEAM_ANNOTATION,
)

SENTRY_API_TOKEN_KEY = "API_TOKEN"
SENTRY_API_URL = "API_URL"
SENTRY_ORGANIZATION = "ORGANIZATION"
SENTRY_DSN_KEY = "SENTRY_DSN"
SENTRY_PROJECT_SLUG_KEY = "SENTRY_PROJECT_SLUG"

SENTRY_VAR_NAMES = (
    ("SENTRY_DSN", SENTRY_DSN_KEY),
)

REQUIRED_SENTRY_SECRET_KEYS = (
    SENTRY_DSN_KEY,
    SENTRY_PROJECT_SLUG_KEY,
)

SENTRY_TRANSFORM_ENVIRONMENTS = {
    "development": "dev",
    "production": "prod",
}
