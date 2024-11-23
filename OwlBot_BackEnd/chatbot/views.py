from django.shortcuts import render, redirect  # type: ignore
from django.http import JsonResponse  # type: ignore
from django.contrib.auth import authenticate, login, logout  # type: ignore
from django.contrib.auth.decorators import login_required  # type: ignore
from django.contrib import messages  # type: ignore
from django.contrib.auth.models import User # type: ignore
from .query_handler import get_response
from django.views.decorators.csrf import csrf_exempt  # type: ignore
import json
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from .scheduler import add_one_time_task, add_recurring_task, remove_task
from django.views import View #type:ignore
from django.utils.decorators import method_decorator #type:ignore


@csrf_exempt
def chatbot_query(request):
    if request.method == "POST":
        try:
            # Parse JSON body
            data = json.loads(request.body)

            # Extract 'user_input' from JSON
            user_query = data.get("user_input")

            if user_query:
                # Get chat history from session
                chat_history = request.session.get("chat_history", [])

                # Process the query
                response = get_response(user_query, chat_history)

                # Update chat history
                chat_history.append({"user": user_query, "assistant": response})

                # Save updated chat history in session
                request.session["chat_history"] = chat_history
                return JsonResponse({"response": response})

            return JsonResponse({"error": "No input provided"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=400)


@csrf_exempt
def admin_login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
            if not username or not password:
                return JsonResponse(
                    {"error": "Username and password are required."}, status=400
                )

            # Authenticate admin user
            user = authenticate(request, username=username, password=password)
            if user and user.is_staff:  # Check if the user is an admin
                refresh = RefreshToken.for_user(user)
                return JsonResponse(
                    {
                        "token": str(refresh.access_token),
                        "refresh": str(refresh),
                        "username": user.username,
                    }
                )
            else:
                return JsonResponse(
                    {"error": "Invalid credentials or not an admin."}, status=401
                )
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=400)


@method_decorator(csrf_exempt, name="dispatch")
class ScheduleTaskView(View):
    """
    Handles scheduling tasks (one-time and recurring).
    """
    def post(self, request):
        try:
            data = json.loads(request.body)
            task_type = data.get("task_type")  # 'one_time' or 'recurring'
            run_date = data.get("run_date")  # Required for one-time tasks
            cron_expression = data.get("cron_expression")  # Required for recurring tasks

            if task_type == "one_time" and run_date:
                add_one_time_task(run_date)
                return JsonResponse({"message": "One-time task scheduled!"}, status=201)
            elif task_type == "recurring" and cron_expression:
                cron_dict = eval(cron_expression)  # Convert string to dictionary
                add_recurring_task(cron_dict)
                return JsonResponse({"message": "Recurring task scheduled!"}, status=201)
            else:
                return JsonResponse({"error": "Invalid task_type or missing parameters."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def delete(self, request):
        try:
            data = json.loads(request.body)
            job_id = data.get("job_id")
            if not job_id:
                return JsonResponse({"error": "Job ID is required."}, status=400)
            remove_task(job_id)
            return JsonResponse({"message": "Task removed successfully!"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        
    def get(self, request):
        """List all scheduled tasks."""
        try:
            from .scheduler import scheduler
            jobs = scheduler.get_jobs()
            tasks = [
                {"job_id": job.id, "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None}
                for job in jobs
            ]
            return JsonResponse({"tasks": tasks}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        

        
@csrf_exempt
def admin_logout(request):
    if request.method == "POST":
        return JsonResponse({"message": "Logged out successfully."}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=400)
