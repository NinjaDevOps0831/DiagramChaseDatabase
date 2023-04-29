from django.test import TestCase
from neomodel import db, clear_neo4j_database

# Create your tests here.


class DiagramChaseDatabaseTests(TestCase):
    def setUp(self):
        clear_neo4j_database(db)

    def test_single_morphism_in_category(self):
        from .models import Category, Object
               
        C = Category(name='C')
        C.save()
        x = Object(name='x')
        x.save()
        x.category.connect(C)
        C.objects.connect(x)
        y = Object(name='y')
        y.save()
        y.category.connect(C)
        C.objects.connect(y)
        f = x.morphisms.connect(y, {'name' : 'f'})
        f.save()

    