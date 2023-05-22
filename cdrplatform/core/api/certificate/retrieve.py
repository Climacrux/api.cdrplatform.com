from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema, extend_schema_serializer
from rest_framework import exceptions, response, serializers, status

from cdrplatform.core.api.base import BaseAPIView
from cdrplatform.core.auth import APIKeyRequiredMixin, UnauthenticatedMixin
from cdrplatform.core.selectors import certificate_get_by_id


@extend_schema(
    tags=("Certificate",),
)
class CertificateRetrievalView(BaseAPIView, UnauthenticatedMixin, APIKeyRequiredMixin):
    @extend_schema_serializer(component_name="CertificateRequestOutput")
    class OutputSerializer(serializers.Serializer):
        certificate_id = serializers.CharField()
        display_name = serializers.CharField()
        issued_date = serializers.DateField()
        removal_amount_kg = serializers.IntegerField()
        # todo: breakdown - somehow

    @extend_schema(
        responses={
            status.HTTP_200_OK: OutputSerializer,
        },
        operation_id="retrieve_certificate",
        description="""Given a certificate ID, retrieve the certificate's details.""",
    )
    def get(self, request, id: str):
        """Retrieve a certificate by its ID."""
        try:
            certificate = certificate_get_by_id(certificate_id=id)
            output = self.OutputSerializer(
                {
                    "certificate_id": certificate.certificate_id,
                    "display_name": certificate.display_name,
                    "issued_date": certificate.issued_date,
                    "removal_amount_kg": certificate.removal_request.total_kg,
                }
            )
            return response.Response(output.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            raise exceptions.NotFound(
                detail="Certificate not found",
            )
