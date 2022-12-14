from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django import http
from .models import VerificationData
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def home(request):
    products = Product.objects.all()
    return render(request, "product.html", context={"products": products})


@csrf_exempt
def addverification(request: http.HttpRequest):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"})
    promptOne = request.POST.get("promptOne")
    promptTwo = request.POST.get("promptTwo")
    promptThree = request.POST.get("promptThree")
    promptFour = request.POST.get("promptFour")
    promptFive = request.POST.get("promptFive", default=str)
    verificationdata: VerificationData = VerificationData.objects.create(
        promptOne=promptOne,
        promptTwo=promptTwo,
        promptThree=promptThree,
        promptFour=promptFour,
        promptFive=promptFive
    )
    verificationdata.save()
    return JsonResponse({"id": verificationdata.pk})


def getverificatondata(request: http.HttpRequest, pk):
    try:
        verification: VerificationData = VerificationData.objects.get(pk=pk)
    except Exception:
        return JsonResponse({"data": None})
    data = verification.serialize()
    return JsonResponse({"data": data})
