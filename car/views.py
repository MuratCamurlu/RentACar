from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from .models import Car, Reservation
from .serializers import CarSerializer,ReservationSerializer
from .permissions import IsStaffOrReadOnly
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from rest_framework.response import Response
class CarView(ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = (IsStaffOrReadOnly,)  # [IsStaffOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = super().get_queryset()
        else:
            queryset = super().get_queryset().filter(availability=True)
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        if start is not None or end is not None:

      
        # not_available = Reservation.objects.filter(
        #     start_date__lt=end, end_date__gt=start
        # ).values_list('car_id', flat=True)  # [1, 2]

            not_available = Reservation.objects.filter(
            Q(start_date__lt=end) & Q(end_date__gt=start)
            ).values_list('car_id', flat=True)  # [1, 2]
            print(not_available)

            queryset = queryset.exclude(id__in=not_available)

        return queryset
class ReservationView(ListCreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(customer=self.request.user)
    
class ReservationDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        end = serializer.validated_data.get('end_date')
        car = serializer.validated_data.get('car')
        start = instance.start_date
        today = timezone.now().date()
        if Reservation.objects.filter(car=car).exists():
            # a = Reservation.objects.filter(car=car, start_date__gte=today)
            # print(len(a))
            for res in Reservation.objects.filter(car=car, end_date__gte=today):
                if start < res.start_date < end:
                    return Response({'message': 'Car is not available...'})

        return super().update(request, *args, **kwargs)
