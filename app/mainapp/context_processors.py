from app.mainapp.models import Signup, Politician

def display_post(request):
    return {'display_post' : Post.objects.filter(published=1).order_by("-created_at")[0]}


