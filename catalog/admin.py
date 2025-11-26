from django.contrib import admin
from .models import *


# admin.site.register(Category)
# admin.site.register(Brand)
# admin.site.register(Attribute)
# admin.site.register(AttributeValue)
# admin.site.register(Product)
# admin.site.register(ProductVariant)
# admin.site.register(ProductImage)
# admin.site.register(ProductVideo)


# catalog/admin.py
from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import redirect, render
from django import forms

from .models import (
    Category, Brand, Attribute, AttributeValue,
    Product, ProductVariant, ProductImage, ProductVideo
)
# from .utils import generate_variants_for_product


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'variant', 'role', 'position')
    readonly_fields = ()


class ProductVideoInline(admin.TabularInline):
    model = ProductVideo
    extra = 0
    fields = ('video', 'position')


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    fields = ('sku', 'price', 'inventory_quantity', 'attributes', 'is_active')
    readonly_fields = ('sku',)
    extra = 0
    show_change_link = True

# class ProductSingleInline(admin.TabularInline):
#     model = SingleProduct
#     fields = ('price', 'discount_price', 'cost_price', 'inventory_quantity')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'product_type', 'sku', 'status')
    search_fields = ('title', 'sku')
    inlines = [ProductVariantInline, ProductImageInline, ProductVideoInline]
    # change_form_template = "admin/catalog/product_change_form.html"  # optional custom template for button

    # def get_urls(self):
    #     urls = super().get_urls()
    #     custom_urls = [
    #         path('<path:object_id>/generate_variants/', self.admin_site.admin_view(self.generate_variants_view), name='catalog_product_generate_variants'),
    #     ]
    #     return custom_urls + urls

    # def generate_variants_view(self, request, object_id):
    #     product = self.get_object(request, object_id)
    #     if request.method == "POST":
    #         # form fields expect attribute ids and comma separated values per attribute
    #         # e.g., attribute_1 = "S,M", attribute_2 = "Red,Black"
    #         attribute_values_map = {}
    #         for k, v in request.POST.items():
    #             if k.startswith("attribute_"):
    #                 aid = int(k.split("_")[1])
    #                 values = [x.strip() for x in v.split(",") if x.strip()]
    #                 attribute_values_map[aid] = values
    #         created = generate_variants_for_product(product, attribute_values_map)
    #         messages.success(request, f"{len(created)} variants created/updated for {product.title}")
    #         return redirect(f"../../{object_id}/change/")
    #     else:
    #         # show simple form to input attribute values
    #         attr_qs = Attribute.objects.filter(is_variant=True)
    #         context = dict(
    #             self.admin_site.each_context(request),
    #             product=product,
    #             attrs=attr_qs,
    #         )
    #         return render(request, "admin/catalog/generate_variants.html", context)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'sort_order')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'is_variant', 'is_filterable')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'attribute', 'value', 'sort_order')
    list_filter = ('attribute',)
    search_fields = ('value',)


admin.site.register(ProductVariant)
# admin.site.register(SingleProduct)
admin.site.register(ProductImage)
admin.site.register(ProductVideo)
