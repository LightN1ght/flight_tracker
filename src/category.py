class Category:
    category_count = 0
    product_count = 0

    name: str
    description: str

    def __init__(self, name, description, products):
        self.name = name
        self.description = description
        self.__products = list(products)
        Category.product_count += len(self.__products)
        Category.category_count += 1

    def add_product(self, product):
        self.__products.append(product)
        Category.product_count += 1

    @property
    def products(self):
        lines = []
        for product in self.__products:
            lines.append(
                f"{product.name}, {product.price} руб. Остаток: {product.quantity} шт.\n"
            )
        return "".join(lines)
