import logging

import kopf

from exceptions import InfrastructureServiceProblem
from observability.metrics.decorator import monitoring, mutation_hook_monitoring
from operators.dto import ConnectorStatus, MutationHookStatus
from connectors.keycloak_connector.services.keycloak_connector import \
    KeycloakConnectorService
from connectors.keycloak_connector.exceptions import KeycloakConnectorError
from connectors.keycloak_connector.factories.dto_factory import \
    KeycloakConnectorMicroserviceDtoFactory as DtoFactory
from connectors.keycloak_connector.factories.service_factories.keycloak_connector import \
    KeycloakConnectorServiceFactory
from utils.common import OwnerReferenceDto, get_owner_reference


@kopf.on.mutate("pods.v1", id="kk-con-on-createpods")
@monitoring(connector_type='keycloak_connector')
def create_pods(body, patch, spec, annotations, **_):
    # At the time of the creation of Pod, the name and uid were not yet
    # set in the manifest, so in the logs we refer to its owner.
    owner_ref: OwnerReferenceDto = get_owner_reference(body)
    owner_fmt = f"{owner_ref.kind}: {owner_ref.name}" if owner_ref else ""

    logging.info(f"[{owner_fmt}] Keycloak mutate handler is called on pod creating")
    status = ConnectorStatus(
        is_used=KeycloakConnectorService.is_kk_conn_used_by_obj(annotations)
    )
    if not status.is_used:
        logging.info(f"[{owner_fmt}] Keycloak connector is not used, "
                     "because not expected annotations")
        return status

    kk_conn_service = KeycloakConnectorServiceFactory.create()
    ms_keycloak_conn = DtoFactory.dto_from_metadata(annotations)
    logging.info(f"[{owner_fmt}] Keycloak connector service is created")
    try:
        kk_conn_service.on_create_deployment(ms_keycloak_conn)
        logging.info(f"[{owner_fmt}] Keycloak connector service was processed in infrastructure")
    except KeycloakConnectorError as e:
        logging.error(f"[{owner_fmt}] Problem with Keycloak connector", exc_info=e)
        status.is_enabled = False
        status.exception = e
    except InfrastructureServiceProblem as e:
        logging.error(f"[{owner_fmt}] Problem with infrastructure, "
                      "some changes couldn't be applied",
                      exc_info=e)
        status.is_enabled = True
        status.exception = e
    else:
        status.is_enabled = True
        if kk_conn_service.mutate_containers(spec, ms_keycloak_conn):
            patch.spec["containers"] = spec.get("containers", [])
            patch.spec["initContainers"] = spec.get("initContainers", [])
            logging.info(f"[{owner_fmt}] Keycloak connector service patched containers, "
                         f"patch.spec: {patch.spec}")
    return status


@kopf.on.create("pods.v1", id="keycloak-connector-on-check-creation")
@mutation_hook_monitoring(connector_type="keycloak_connector")
def check_creation(annotations, body, spec, **_):
    status = MutationHookStatus()

    if not KeycloakConnectorService.is_kk_conn_used_by_obj(annotations):
        status.is_used = False
        return status

    status.is_used = True
    status.is_success = True
    if not KeycloakConnectorService.containers_contain_required_envs(spec):
        kopf.event(
            body,
            type="Error",
            reason="KeycloakConnector",
            message="Keycloak Connector not applied",
        )
        status.is_success = False

    return status
