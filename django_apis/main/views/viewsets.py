from datetime import datetime, date
from django.shortcuts import render
from ..models.models import *
from ..util.model_util import check_occurrence
from rest_framework import viewsets, permissions, status
from ..serializers.serializers import *
from itertools import chain
from rest_framework.response import Response


# Create your views here.

class MyScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = MyScheduleSerializer

    permission_classes = [
        permissions.AllowAny
    ]

    def get_queryset(self):
        date_param = self.request.query_params.get('date')
        time_param = self.request.query_params.get('time')
        user_id = self.request.query_params.get('u_id')
        # content = self.request.query_params.get('content')
        queryset = MySchedule.objects.filter(user_id=user_id)

        if date_param is not None or time_param is not None:
            if date_param is None:
                date_param = date.today()
            else:
                date_param = datetime.strptime(date_param, "%d-%m-%Y").date()

            exception_queryset = ScheduleInstanceException.objects \
                .filter(user_id=user_id) \
                .filter(date_field=date_param)

            queryset = queryset.exclude(id__in=[e.schedule_id for e in exception_queryset])
            queryset = queryset.filter(id__in=[s.id for s in queryset if check_occurrence(date_param, s)])

            if time_param is not None:
                time_param = datetime.strptime(time_param, "%H:%M")
                queryset = queryset.exclude(start_time__gt=time_param).exclude(end_time__lt=time_param)

        return queryset

    def destroy(self, request, *args, **kwargs):
        schedule = self.get_object()
        date_param = self.request.query_params.get("date")
        if schedule.is_recurring is False:
            schedule.delete()
            return Response({"message": "Delete success"})
        else:
            if date_param is None:
                message = {"err_message": "No date parameter in request"}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            else:
                date_param = datetime.strptime(date_param, "%d-%m-%Y").date()

                schedule_exception = ScheduleInstanceException.objects.create(schedule_id=schedule.pk,
                                                                              date_field=date_param,
                                                                              time_field=schedule.time_field,
                                                                              content=schedule.content,
                                                                              user_id=schedule.user_id)
                schedule_exception.save()

                serializer = ScheduleInstanceExceptionSerializer(schedule_exception)

                return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        schedule = self.get_object()
        date_param = self.request.query_params.get('date')

        data = request.data

        if schedule.is_recurring is False:
            schedule.date_field = data['date_field']
            schedule.time_field = data['time_field']
            schedule.content = data['content']

            schedule.save()

            serializer = MyScheduleSerializer(schedule)

            return Response(data=serializer.data)
        else:
            if date_param is None:
                message = {"err_message": "No date parameter in request"}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            else:
                date_param = datetime.strptime(date_param, "%d-%m-%Y").date()

                schedule_exception = ScheduleInstanceException.objects.create(schedule_id=schedule.pk,
                                                                              date_field=date_param,
                                                                              time_field=schedule.time_field,
                                                                              content=schedule.content,
                                                                              user_id=schedule.user_id)
                schedule_exception.save()

                schedule_new = schedule.objects.create(date_field=data['date_field'],
                                                       time_field=data['time_field'],
                                                       content=data['content'],
                                                       user_id=schedule.user_id)

                schedule_new.save()

                serializer = MyScheduleSerializer(schedule_new)

                return Response(data=serializer.data)
    # def destroy(self, request, *args, **kwargs):
    #     # print('delete')
    #     schedule = self.get_object()
    #     if schedule.is_recurring is True:
    #         # print('is recurring')
    #         schedule.recurrence_end_date = date.today()
    #         schedule.save()
    #     else:
    #         # print('call super')
    #         super(MyScheduleViewSet, self).destroy(request, *args, **kwargs)
    #     return Response(status=status.HTTP_204_NO_CONTENT)


class ScheduleInstanceExceptionViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduleInstanceExceptionSerializer

    permission_classes = [
        permissions.AllowAny
    ]


class ReminderViewSet(viewsets.ModelViewSet):
    serializer_class = ReminderSerializer

    permission_classes = [
        permissions.AllowAny
    ]

    def get_queryset(self):
        date_param = self.request.query_params.get('date')
        time_param = self.request.query_params.get('time')
        user_id = self.request.query_params.get('u_id')

        queryset = Reminder.objects.filter(user_id=user_id)
        if date_param is not None or time_param is not None:
            if date_param is None:
                date_param = date.today()
            else:
                date_param = datetime.strptime(date_param, "%d-%m-%Y").date()

            exception_queryset = ReminderInstanceException.objects \
                .filter(user_id=user_id) \
                .filter(date_field=date_param)

            queryset = queryset.exclude(id__in=[e.reminder_id for e in exception_queryset])
            queryset = queryset.filter(id__in=[s.id for s in queryset if check_occurrence(date_param, s)])

            if time_param is not None:
                time_param = datetime.strptime(time_param, "%H:%M")
                queryset = queryset.filter(time_field=time_param)

        return queryset

    def destroy(self, request, *args, **kwargs):
        reminder = self.get_object()
        date_param = self.request.query_params.get("date")
        if reminder.is_recurring is False:
            reminder.delete()
            return Response({"message": "Delete success"})
        else:
            if date_param is None:
                message = {"err_message": "No date parameter in request"}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            else:
                date_param = datetime.strptime(date_param, "%d-%m-%Y").date()

                reminder_exception = ReminderInstanceException.objects.create(reminder_id=reminder.pk,
                                                                              date_field=date_param,
                                                                              time_field=reminder.time_field,
                                                                              content=reminder.content,
                                                                              user_id=reminder.user_id)
                reminder_exception.save()

                serializer = ReminderInstanceExceptionSerializer(reminder_exception)

                return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        reminder = self.get_object()
        date_param = self.request.query_params.get('date')

        data = request.data

        if reminder.is_recurring is False:
            reminder.date_field = data['date_field']
            reminder.time_field = data['time_field']
            reminder.content = data['content']

            reminder.save()

            serializer = ReminderSerializer(reminder)

            return Response(data=serializer.data)
        else:
            if date_param is None:
                message = {"err_message": "No date parameter in request"}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            else:
                date_param = datetime.strptime(date_param, "%d-%m-%Y").date()

                reminder_exception = ReminderInstanceException.objects.create(reminder_id=reminder.pk,
                                                                              date_field=date_param,
                                                                              time_field=reminder.time_field,
                                                                              content=reminder.content,
                                                                              user_id=reminder.user_id)
                reminder_exception.save()

                reminder_new = Reminder.objects.create(date_field=data['date_field'],
                                                       time_field=data['time_field'],
                                                       content=data['content'],
                                                       user_id=reminder.user_id)

                reminder_new.save()

                serializer = ReminderSerializer(reminder_new)

                return Response(data=serializer.data)


class ReminderInstanceExceptionViewSet(viewsets.ModelViewSet):
    serializer_class = ReminderInstanceExceptionSerializer

    permission_classes = [
        permissions.AllowAny
    ]


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer

    permission_classes = [
        permissions.AllowAny
    ]

    def get_queryset(self):
        time_param1 = self.request.query_params.get("time1")
        time_param2 = self.request.query_params.get("time2")
        date_param = self.request.query_params.get("date")
        user_id = self.request.query_params.get('u_id')

        queryset = Task.objects.filter(user_id=user_id)
        if time_param1 is not None or time_param2 is not None or date_param is not None:
            if date_param is None:
                date_param = date.today()
            else:
                date_param = datetime.strptime(date_param, "%d-%m-%Y").date()

            queryset = queryset.filter(date_field=date_param)

            if time_param1 is not None:
                if time_param2 is not None:
                    queryset = queryset.filter(time_field__gte=time_param1).filter(time_param2__lte=time_param2)
                else:
                    queryset = queryset.filter(time_field=time_param1)

        return queryset
