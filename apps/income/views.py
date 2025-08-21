from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.db.models import Sum, Avg, Count, Q
from django.db.models.functions import TruncMonth, TruncWeek
from datetime import datetime, timedelta, date
from .models import DailyIncome
from .serializers import (
    DailyIncomeSerializer, 
    DailyIncomeCreateSerializer, 
    DailyIncomeListSerializer
)
from apps.core.permissions import IsAdminUser


class DailyIncomeViewSet(viewsets.ModelViewSet):
    """
    Income management with proper permissions and analytics
    """
    queryset = DailyIncome.objects.select_related('grocery', 'recorded_by')
    serializer_class = DailyIncomeSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['grocery', 'date', 'recorded_by']
    search_fields = ['grocery__name', 'notes']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date']
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if self.request.user.user_type == 'supplier':
            try:
                supplier_profile = self.request.user.supplier_profile
                if supplier_profile.assigned_grocery:
                    return queryset.filter(grocery=supplier_profile.assigned_grocery)
            except AttributeError:
                pass
            return queryset.none()
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DailyIncomeCreateSerializer
        elif self.action == 'list':
            return DailyIncomeListSerializer
        return DailyIncomeSerializer
    
    def perform_create(self, serializer):
        """Create income record with proper validation"""
        user = self.request.user
        
        if user.user_type == 'supplier':
            try:
                supplier_profile = user.supplier_profile
                grocery = serializer.validated_data['grocery']
                if supplier_profile.assigned_grocery != grocery:
                    raise PermissionError("Cannot add income for other grocery stores")
            except AttributeError:
                raise PermissionError("Supplier profile not found")
        
        serializer.save(recorded_by=user)
    
    def perform_update(self, serializer):
        """Only admins can update income records"""
        if self.request.user.user_type != 'admin':
            raise PermissionError("Only admins can modify income records")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Only admins can delete income records"""
        if self.request.user.user_type != 'admin':
            raise PermissionError("Only admins can delete income records")
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Comprehensive income analytics"""
        queryset = self.get_queryset()
        

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        grocery_id = request.query_params.get('grocery_id')
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                return Response({'error': 'Invalid start_date format. Use YYYY-MM-DD'}, 
                              status=status.HTTP_400_BAD_REQUEST)
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                return Response({'error': 'Invalid end_date format. Use YYYY-MM-DD'}, 
                              status=status.HTTP_400_BAD_REQUEST)
        
        if grocery_id:
            queryset = queryset.filter(grocery_id=grocery_id)
        
        analytics = queryset.aggregate(
            total_income=Sum('amount') or 0,
            average_daily_income=Avg('amount') or 0,
            total_records=Count('id'),
            max_daily_income=queryset.aggregate(max_amount=models.Max('amount'))['max_amount'] or 0,
            min_daily_income=queryset.aggregate(min_amount=models.Min('amount'))['min_amount'] or 0
        )
        
        analytics.update({
            'date_range': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
            }
        })
        
        return Response(analytics)
    
    @action(detail=False, methods=['get'])
    def monthly_report(self, request):
        """Detailed monthly income report"""
        try:
            year = int(request.query_params.get('year', datetime.now().year))
            month = int(request.query_params.get('month', datetime.now().month))
        except (ValueError, TypeError):
            return Response({'error': 'Invalid year or month parameter'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(
            date__year=year,
            date__month=month
        )
        
        daily_data = {}
        total_amount = 0
        
        for income in queryset:
            day = income.date.day
            amount = float(income.amount)
            if day not in daily_data:
                daily_data[day] = {
                    'amount': 0,
                    'records_count': 0
                }
            daily_data[day]['amount'] += amount
            daily_data[day]['records_count'] += 1
            total_amount += amount
        

        grocery_breakdown = {}
        if request.user.user_type == 'admin':
            grocery_totals = queryset.values('grocery__name').annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('-total')
            
            for item in grocery_totals:
                grocery_breakdown[item['grocery__name']] = {
                    'total': float(item['total']),
                    'records': item['count']
                }
        
        return Response({
            'year': year,
            'month': month,
            'daily_breakdown': daily_data,
            'grocery_breakdown': grocery_breakdown,
            'summary': {
                'total_income': total_amount,
                'total_days_recorded': len(daily_data),
                'average_daily': total_amount / len(daily_data) if daily_data else 0
            }
        })
    
    @action(detail=False, methods=['get'])
    def weekly_trends(self, request):
        """Weekly income trends"""
        weeks_back = int(request.query_params.get('weeks', 4))
        end_date = date.today()
        start_date = end_date - timedelta(weeks=weeks_back)
        
        queryset = self.get_queryset().filter(
            date__gte=start_date,
            date__lte=end_date
        )
        
        weekly_data = queryset.annotate(
            week=TruncWeek('date')
        ).values('week').annotate(
            total_income=Sum('amount'),
            record_count=Count('id')
        ).order_by('week')
        

        trends = []
        for week in weekly_data:
            trends.append({
                'week_start': week['week'].strftime('%Y-%m-%d'),
                'total_income': float(week['total_income']),
                'records_count': week['record_count']
            })
        
        return Response({
            'period': f"{start_date} to {end_date}",
            'weekly_trends': trends
        })
    
    @action(detail=False, methods=['get'])
    def my_income_summary(self, request):
        """Supplier's own income summary"""
        if request.user.user_type != 'supplier':
            return Response({'error': 'Only suppliers can access this endpoint'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        try:
            supplier_profile = request.user.supplier_profile
            if not supplier_profile.assigned_grocery:
                return Response({'error': 'No grocery assigned'}, 
                              status=status.HTTP_404_NOT_FOUND)
            
            # Get last 30 days
            thirty_days_ago = date.today() - timedelta(days=30)
            queryset = self.get_queryset().filter(date__gte=thirty_days_ago)
            
            summary = queryset.aggregate(
                total_30_days=Sum('amount') or 0,
                average_daily=Avg('amount') or 0,
                total_records=Count('id')
            )
            
            summary.update({
                'grocery_name': supplier_profile.assigned_grocery.name,
                'period': f"Last 30 days ({thirty_days_ago} to {date.today()})"
            })
            
            return Response(summary)
            
        except AttributeError:
            return Response({'error': 'Supplier profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
