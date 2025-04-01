from django.core.management import BaseCommand
from agent.models import *


class TestOrder(BaseCommand):
    help = 'Test Order'

    def add_arguments(self, parser):
        parser.add_argument("method", type=str, help="call method")

    def delete(self):
        print('delete')
        clss = [OrderProduct, LicenseProject, InvoiceProject, TaxProject, Project, Order, Product, User]
        for cls in clss:
            cls.objects.all().delete()

    def create(self):
        user_liwei = User.objects.create(name='李伟')
        user_lifeifei = User.objects.create(name='李费费')

        product_license = Product.objects.create(name='启照', amount=1000)
        product_invoice = Product.objects.create(name='开票', amount=2000)
        product_tax = Product.objects.create(name='报税', amount=3000)

        # liwei
        ratio = 0.8
        order = Order()
        order.amount = ratio * (product_license.amount + product_invoice.amount)
        order.save()

        project_license = LicenseProject.objects.create(name='李伟启照', user=user_liwei, address='天津市滨海新区响螺湾')
        project_invoice = InvoiceProject.objects.create(name='李伟开票任务', user=user_liwei, creditid='89320204239544')

        OrderProduct.objects.create(order=order, product=product_license, amount=product_license.amount * ratio, project=project_license)
        OrderProduct.objects.create(order=order, product=product_invoice, amount=product_invoice.amount * ratio, project=project_invoice)

        # lifeifei
        ratio = 0.5
        order = Order()
        order.amount = ratio * (product_invoice.amount + product_tax.amount)
        order.save()

        project_invoice = InvoiceProject.objects.create(name='李费费开票', user=user_lifeifei, creditid='7423962079432X')
        project_tax = TaxProject.objects.create(name='李费费报税', user=user_lifeifei, creditid='7423962079432X', password='123456L')

        OrderProduct.objects.create(order=order, product=product_invoice, amount=product_invoice.amount * ratio, project=project_invoice)
        OrderProduct.objects.create(order=order, product=product_tax, amount=product_tax.amount * ratio, project=project_tax)

    def get_orders(self):
        for order in Order.objects.filter(amount__gt=1000, products__name='报税').distinct():
            print(order)

    def get_orders2(self):
        print(Order.objects.filter(status__in=[0, 32], products__name='报税', projects__user__name='李伟').distinct().query)
        for order in Order.objects.filter(status__in=[0, 32], products__name='开票', projects__user__name='李伟').distinct():
            print(type(order), order)

    def get_order_products(self):
        order = Order.objects.first()
        for product in order.products.all():
            print(product)

    def get_order_projects(self):
        order = Order.objects.first()
        for project in order.projects.all():
            print(type(project), project, project.orderproduct, project.orderproduct.product, project.order)

    def get_all_orders(self):
        for order in Order.objects.all():
            print('=' * 30)
            print(order)
            for orderproduct in order.orderproduct_set.all():
                amount = orderproduct.amount
                product = orderproduct.product
                project = orderproduct.project
                print(amount, "\t", product, "\t", project.classname, project)

    def get_projects(self):
        projects = InvoiceProject.objects.all()
        for project in projects:
            print(project)

    def handle(self, *args, **options):
        method = options['method']
        getattr(self, method)()
