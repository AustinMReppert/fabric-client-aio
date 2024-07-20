from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field


class WorkspaceType(str, Enum):
    admin_workspace = "AdminWorkspace"
    personal = "Personal"
    workspace = "Workspace"


class Workspace(BaseModel):
    capacity_id: str | None = Field(default=None, alias="capacityId")
    description: str
    display_name: str = Field(alias="displayName")
    id: str | None = Field(default=None)
    type: WorkspaceType = Field(alias="type")


class Workspaces(BaseModel):
    continuation_token: str | None = Field(default=None, alias="continuationToken")
    continuation_uri: str | None = Field(default=None, alias="continuationUri")
    value: list[Workspace]


class CapacityAssignmentProgress(str, Enum):
    completed = "Completed"
    failed = "Failed"
    in_progress = "InProgress"


class WorkspaceIdentity(BaseModel):
    application_id: str = Field(alias="applicationId")
    service_principal_id: str = Field(alias="servicePrincipalId")


class WorkspaceInfo(BaseModel):
    capacity_assignment_progress: CapacityAssignmentProgress = Field(alias="capacityAssignmentProgress")
    capacity_id: str = Field(alias="capacityId")
    description: str
    display_name: str = Field(alias="displayName")
    id: str
    type: WorkspaceType = Field(alias="type")
    workspace_identity: WorkspaceIdentity | None = Field(default=None, alias="workspaceIdentity")


class Items(BaseModel):
    continuation_token: str | None = Field(default=None, alias="continuationToken")
    continuation_uri: str | None = Field(default=None, alias="continuationUri")
    value: list[Item]


class Item(BaseModel):
    description: str
    display_name: str = Field(alias="displayName")
    id: str
    type: ItemType
    workspace_id: str = Field(alias="workspaceId")


class ItemType(str, Enum):
    dashbaord = "Dashboard"
    data_pipeline = "DataPipeline"
    datamart = "Datamart"
    environment = "Environment"
    eventhosue = "Eventhouse"
    eventstream = "Eventstream"
    kql_database = "KQLDatabase"
    kql_queryset = "KQLQueryset"
    lakehouse = "Lakehouse"
    ml_experiment = "MLExperiment"
    ml_model = "MLModel"
    mirrored_warehouse = "MirroredWarehouse"
    notebook = "Notebook"
    paginated_report = "PaginatedReport"
    report = "Report"
    sql_endpoint = "SQLEndpoint"
    semantic_model = "SemanticModel"
    spark_job_definition = "SparkJobDefinition"
    warehouse = "Warehouse"


class ErrorRelatedResource(BaseModel):
    resouce_id: str = Field(alias="resourceId")
    resource_type: str = Field(alias="resourceType")

class ErrorResponseDetails(BaseModel):
    error_code: str = Field(alias="errorCode")
    message: str
    related_resource: str = Field(alias="relatedResource")

class ErrorResponse(BaseModel):
    error_code: str = Field(alias="errorCode")
    message: str
    more_details: list[ErrorResponseDetails] = Field(alias="moreDetails")
    related_resource: ErrorRelatedResource = Field(alias="relatedResource")
    request_id: str = Field(alias="requestId")

class LongRunningOperationStatus(str, Enum):
    failed = "Failed"
    not_started = "NotStarted"
    running = "Running"
    succeeded = "Succeeded"
    undefined = "Undefined"

class OperationState(BaseModel):
    created_time_utc: str = Field(alias="createdTimeUtc")
    error: ErrorResponse | None = Field(default=None)
    last_updated_time_utc: str = Field(alias="lastUpdatedTimeUtc")
    percent_complete: int = Field(alias="percentComplete")
    status: LongRunningOperationStatus

    def is_completed(self) -> bool:
        """Check if the operation is completed."""
        return self.status in (LongRunningOperationStatus.succeeded, LongRunningOperationStatus.failed)
