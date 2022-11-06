from django.db import connections
from django.db.utils import OperationalError
from rest_framework import serializers, status
from rest_framework.response import Response

from .base import BaseAPIView


class HealthView(BaseAPIView):
    """Health endpoint used to check DB connection, liveness etc."""

    db_conns_to_check = ("default",)

    class OutputSerializer(serializers.Serializer):
        db_up = serializers.DictField()

    def has_db_connection(self, db_name: str = "default") -> bool:
        db_conn = connections[db_name]
        try:
            _ = db_conn.cursor()
        except OperationalError:
            connected = False
        else:
            connected = True
        return connected

    def get(self, request):
        db_conn_info = {}
        status_code = status.HTTP_200_OK
        for db in self.db_conns_to_check:
            db_up = self.has_db_connection(db)
            db_conn_info[db] = db_up

            if not db_up:
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        output = self.OutputSerializer({"db_up": db_conn_info})
        return Response(output.data, status=status_code)
