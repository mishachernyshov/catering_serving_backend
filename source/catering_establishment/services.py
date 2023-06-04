from catering_establishment import serializers as ce_serializers


def create_catering_establishment_with_related_models(data):
    serializer = ce_serializers.CateringEstablishmentSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.save()


def create_booking(data):
    serializer = ce_serializers.BookingWriteSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.data


def get_establishments_tables(queryset):
    return {
        establishment.id: (ce_serializers.CateringEstablishmentTableSerializer(establishment.tables, many=True).data)
        for establishment in queryset
    }


def get_establishments_work_hours(queryset):
    return {
        work_hours.catering_establishment.id: (ce_serializers.WorkHoursSerializer(work_hours).data)
        for work_hours in queryset
    }
