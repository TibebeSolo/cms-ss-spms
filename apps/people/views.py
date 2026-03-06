from django.http import HttpResponse
from .services import EthiopianDateService
from django.views.generic import TemplateView

def hx_convert_eth_date(request):
    """
    HTMX endpoint that receives Eth Year, Month, and Day.
    Returns an HTML span with the Gregorian equivalent.
    """
    # Extract the dynamic field names sent by hx-include
    y = request.GET.get('eth_year')
    m = request.GET.get('eth_month')
    d = request.GET.get('eth_day')

    if y and m and d:
        try:
            date_str = f"{int(y)}-{int(m)}-{int(d)}"
            greg_date = EthiopianDateService.ethiopian_to_gregorian(date_str)
            
            if greg_date:
                formatted_date = greg_date.strftime('%d %B %Y')
                return HttpResponse(
                    f"<span class='text-success small fw-bold'><i class='bi bi-check-circle'></i> Gregorian: {formatted_date}</span>"
                )
        except ValueError:
            pass # Invalid date combination (e.g., Pagume 6 on a non-leap year)

    return HttpResponse(
        "<span class='text-muted small'><i class='bi bi-info-circle'></i> Enter a valid Ethiopian date to see Gregorian equivalent.</span>"
    )

