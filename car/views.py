from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from .models import Car, Reservation
from .serializers import CarSerializer,ReservationSerializer
from .permissions import IsStaffOrReadOnly

from django.db.models import Q


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