"""Session-backed cart: { product_id_str: { qty, color, size } }"""


def get_cart(request):
    cart = request.session.get("cart")
    if cart is None:
        cart = {}
        request.session["cart"] = cart
    return cart


def cart_count(request):
    cart = get_cart(request)
    return sum(int(v.get("qty", 0)) for v in cart.values())


def add_item(request, product_id, quantity, color="", size=""):
    cart = get_cart(request)
    key = str(product_id)
    cart[key] = {
        "qty": int(quantity),
        "color": color or "",
        "size": size or "",
    }
    request.session.modified = True


def update_qty(request, product_id, quantity):
    cart = get_cart(request)
    key = str(product_id)
    if key not in cart:
        return
    if quantity <= 0:
        del cart[key]
    else:
        cart[key]["qty"] = int(quantity)
    request.session.modified = True


def remove_item(request, product_id):
    cart = get_cart(request)
    key = str(product_id)
    if key in cart:
        del cart[key]
        request.session.modified = True


def clear_cart(request):
    request.session["cart"] = {}
    request.session.modified = True
