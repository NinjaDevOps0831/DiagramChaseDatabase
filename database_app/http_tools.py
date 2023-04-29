from .models import Diagram
#from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
from django.core.exceptions import ObjectDoesNotExist


def get_diagram(request, **kwargs):    
    diagram = Diagram.nodes.get_or_none(**kwargs)

    if diagram is None:
        raise ObjectDoesNotExist(
            f"""The diagram with the following fields does not exist in the database:\n"""
            f"""{str(kwargs)}""")
    
    session = request.session
    user = request.user.username
    
    if 'diagram' in session:
        if diagram.checked_out_by:  # Yes, test for both None and ''
            if diagram.checked_out_by != user:
                del session['diagram']
                raise Exception(f'User "{diagram.checked_out_by}" already has that diagram checked out for editing.')

    diagram.checked_out_by = user
    diagram.save()
    session['diagram'] = diagram.name            
    return diagram
        