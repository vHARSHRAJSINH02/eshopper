# context_processors.py

from .models import Wishlist, Cart_Items, Category

def counts(request):
    lid = request.session.get('lid')
    wish_ids = 0
    cart_ids = 0

    if lid:
        wish_ids = Wishlist.objects.filter(lid=lid).count()
        cart_ids = Cart_Items.objects.filter(lid=lid, c_Status='pending').count()

    categories = Category.objects.all()
    return {'wishcount': wish_ids, 'cartcount': cart_ids,'categories':categories}

