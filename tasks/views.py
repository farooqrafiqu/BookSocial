from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_celery_results.models import TaskResult

class TaskStatusView(APIView):
    """
    GET /api/tasks/<task_id>/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        try:
            tr = TaskResult.objects.get(task_id=task_id)
        except TaskResult.DoesNotExist:
            return Response({"state": "PENDING"}, status=200)

        data = {
            "state": tr.status,           # PENDING / STARTED / SUCCESS / FAILURE
            "date_done": tr.date_done,
            "result": tr.result,          # we’ll store created book IDs here
        }
        return Response(data)
