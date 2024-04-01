from rest_framework import filters
from django.db import models

class ProductIdNameSearchFilter(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        search_fields = getattr(view, 'search_fields', None)
        search_term = request.query_params.get(self.search_param, '').strip()

        if not search_term or not search_fields:
            return queryset

        # Split the search term into words
        search_terms = search_term.split()

        # Create an empty Q object to gradually add search conditions
        search_conditions = models.Q()

        # Iterate over each search term and add search conditions
        for term in search_terms:
            # Add search conditions for each field in search_fields
            for field_name in search_fields:
                lookup = field_name + '__icontains'
                search_conditions |= models.Q(**{lookup: term})

        return queryset.filter(search_conditions)
