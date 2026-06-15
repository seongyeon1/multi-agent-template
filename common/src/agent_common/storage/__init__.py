"""오브젝트 스토리지 (공통 인프라 stub).

S3 호환 백업/아카이브 자리표시자. 구성값은 ``CommonSettings.s3_*`` 에서 읽고,
``S3_RAW_ARCHIVE_ENABLED`` 토글로 기본 off. 상속 인스턴스가 boto3 구현을 채운다.
"""

from __future__ import annotations

from agent_common.settings import get_common


class ObjectStorage:
    def __init__(self) -> None:
        common = get_common()
        self.enabled = common.s3_enabled
        self.bucket = common.s3_bucket
        self.region = common.s3_region

    def is_active(self) -> bool:
        return self.enabled and self.bucket is not None
