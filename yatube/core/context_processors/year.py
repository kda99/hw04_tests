from datetime import datetime


def year(request):
    currentYear = datetime.now().year
    return {'year': currentYear}
