from django.db import models
from django.conf import settings
from product.models import AlegroGoods
from django.db.models.signals import pre_save, m2m_changed



User = settings.AUTH_USER_MODEL

class CartManager(models.Manager):
    def new_or_get(self, request):
        cart_id = request.session.get('cart_id', None)
        qs = self.get_queryset().filter(id=cart_id)
        if qs.count() == 1:
            new_obj = False
            cart_obj = qs.first()
            if request.user.is_authenticated and cart_obj.user is None:
                cart_obj.user = request.user
                cart_obj.save()
        else:
            cart_obj = Cart.objects.new(user=request.user)
            new_obj = True
            request.session['cart_id'] = cart_obj.pk
        return cart_obj, new_obj

    def just_get(self, request, pk):
        cart_id = pk
        qs = self.get_queryset().filter(id=cart_id)
        cart_obj = qs.first()
        return cart_obj

    def new(self, user=None):
        user_obj = None
        if user is not None:
            if user.is_authenticated:
                user_obj = user
        return self.model.objects.create(user=user_obj)


class Cart(models.Model):
    user            = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    products        = models.ManyToManyField(AlegroGoods, blank=True)
    subtotal        = models.DecimalField(default=0, max_digits=20, decimal_places=0)
    total           = models.DecimalField(default=0, max_digits=20, decimal_places=0)
    updated         = models.DateTimeField(auto_now=True)
    timestamp       = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Корзины'

    objects = CartManager()


    def __str__(self):
        return str(self.id)


def m2m_changed_cart_receiver(sender, instance, action, *args, **kwargs):
    if action == 'post_add' or action == 'post_remove' or action == 'post_clear':
        products = instance.products.all()
        total = 0
        for x in products:
            total += x.price
            
        if instance.subtotal != total:
            instance.subtotal = total
            instance.save()

m2m_changed.connect(m2m_changed_cart_receiver, sender=Cart.products.through)

def pre_save_cart_receiver(sender, instance, *args, **kwargs):
    instance.total = instance.subtotal + 10

pre_save.connect(pre_save_cart_receiver, sender=Cart)
