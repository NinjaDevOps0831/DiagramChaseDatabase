from django.shortcuts import render, redirect, HttpResponse
from .models import Object, Category, Diagram, get_model_by_uid, get_model_class, get_unique
from diagram_chase_database.http_tools import get_posted_text
from django.http import JsonResponse
from diagram_chase_database.python_tools import full_qualname
from django.db import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from diagram_chase_database.settings import DEBUG, MAX_USER_EDIT_DIAGRAMS, MAX_DIAGRAMS_PER_PAGE, MAX_TEXT_LENGTH
from neomodel.properties import StringProperty
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.templatetags.static import static
import base64
import json
from .forms import FunctorForm
import re

# Create your views here.

def embed_diagram(request, diagram_id):
   if request.method == 'GET':
      diagram = get_model_by_uid(Diagram, uid=diagram_id)
      data = diagram.quiver_format()
      data = json.dumps(data)
      data = base64.b64encode(data.encode('utf-8'))         
      diagram.embed_data = f'{static("")}/quiver/src/index.html?q={data.decode()}&embed'
      
      context = {
         'diagram' : diagram
      }
      
      return render(request, 'database_app/embed_diagram.html', context)
   


def load_diagram_from_database(request, diagram_id):
   try:
      if request.method == 'GET':
         diagram = get_model_by_uid(Diagram, uid=diagram_id)
         json_str = json.dumps(diagram.quiver_format())
         
         return HttpResponse(json_str, content_type='text/plain; charset=utf8')
      
   except Exception as e:
      return redirect('error', f'{full_qualname(e)}: {str(e)}')


@login_required   
def save_diagram_to_database(request, diagram_id:str):
   try:
      if request.method != 'POST': #or not request.headers.get("contentType", "application/json; charset=utf-8"):
         raise OperationalError('You can only use the POST method to save to the database.')            
      user = request.user.username

      diagram = get_model_by_uid(Diagram, uid=diagram_id)

      if diagram is None:
         raise ObjectDoesNotExist(f'There exists no diagram with uid "{diagram_id}".') 

      if diagram.checked_out_by != user:
         raise OperationalError(
               f'The diagram with id "{diagram_id}" is already checked out by {diagram.checked_out_by}')                

      body = request.body.decode('utf-8')

      if body:
         try:
            data = json.loads(body)                
         except json.decoder.JSONDecodeError:
            # For some reason, empty diagrams are resulting in the body as a URL str (not JSON)
            data = [0, 0]               
      else:
         data = [0, 0]

      diagram.delete_objects()
      diagram.load_from_editor(data)        
      
      messages.success(request, f'🌩️ Successfully saved diagram (id={diagram.uid}) to the database!')

      return JsonResponse(
           'Wrote the following data to the database:\n' + str(data), safe=False)

   except Exception as e:
      #if DEBUG:
         #raise e
      return JsonResponse({'error_msg' : f'{full_qualname(e)}: {str(e)}'})


def test(request):
   return render(request, 'test.html')

order_by_text_map = {
   'name' : 'name',
   'modified' : 'date modified',
   'created' : 'date created',
}

order_dir_text_map = {
   'asc' : 'Ascending',
   'desc' : 'Descending',
}

@login_required
def my_diagram_list(request, order_by, order_dir, page_num):   
   if order_by not in order_by_text_map or order_dir not in order_dir_text_map:
      return
   
   diagrams = Diagram.nodes
   
   sign = '-' if order_dir == 'desc' else ''
   
   if order_by == 'created':
      diagrams = diagrams.order_by(sign + 'date_created') 
   elif order_by == 'modified':
      diagrams = diagrams.order_by(sign + 'date_modified')
   elif order_by == 'name':
      diagrams = diagrams.order_by(sign + 'name')
  
   diagrams = diagrams.filter(checked_out_by=request.user.username)
      
   num_diagrams = len(diagrams)
   
   N = MAX_DIAGRAMS_PER_PAGE
   num_pages = int(num_diagrams / N) + (1 if num_diagrams % N != 0 else 0)
   
   diagram_list = []
   
   if num_pages != 0:
      page_num %= num_pages
      
      if page_num == num_pages - 1:
         diagrams = diagrams[N*page_num:N*page_num + num_diagrams % N]
      else:
         diagrams = diagrams[N*page_num : N*(page_num + 1)]
   
      for diagram in diagrams:
         data = diagram.quiver_format()
         data = json.dumps(data)
         data = base64.b64encode(data.encode('utf-8')) 
         diagram.embed_data = data.decode()
         diagram_list.append(diagram)
            
   else:
      page_num = 0 
      
   context = {
      'diagrams': diagram_list,
      'num_pages': num_pages,
      'page_num': page_num,
      'next_page' : page_num + 1,
      'prev_page' : page_num - 1,
      'order_by' : order_by,
      'order_dir' : order_dir,
      'order_by_text' : order_by_text_map[order_by],
      'order_dir_text' : order_dir_text_map[order_dir],
   }
   
   return render(request, "database_app/my_diagram_list.html", context)


@login_required
def diagram_editor(request, diagram_id:str):
   try:
      session = request.session
      user = request.user.username

      if 'diagram ids' not in session:
         session['diagram ids'] = []
      else:
         if diagram_id not in session['diagram ids'] and \
               len(session['diagram ids']) == MAX_USER_EDIT_DIAGRAMS:
            raise OperationalError(f"You can't have more than {MAX_USER_EDIT_DIAGRAMS} diagrams checked out.")

      diagram = get_model_by_uid(Diagram, uid=diagram_id)

      if diagram:
         if diagram.name == '':
            raise ValueError('Diagram name must not be empty.')

         if not diagram.checked_out_by:
            diagram.checked_out_by = user
            session['diagram ids'].append(diagram_id)
            session.save()
         else:
            if diagram.checked_out_by != user:
               raise OperationalError(
                       f'The diagram with id "{diagram_id}" is already checked out by {diagram.checked_out_by}')
      else:
         raise ObjectDoesNotExist(f'There exists no diagram with uid "{diagram_id}".')                

      category = diagram.category.single()

      diagram_data = json.dumps(diagram.quiver_format())

      context = {
         'diagram_name' : diagram.name,
         'category_name' : category.name,
         'diagram_id' : diagram.uid,
         'quiver_str' : diagram_data,
         #'commutes_text' : diagram.commutes_text,
      }

      messages.success(request, f'🌩️ Successfully loaded diagram (id={diagram.uid}) from the database!')
      return render(request, 'database_app/diagram_editor.html', context)  

   except Exception as e:
      messages.error(request, f'{full_qualname(e)}: {str(e)}')   
      return redirect('home')
   
   
@login_required
def create_new_diagram(request):   
   diagram = Diagram.our_create(name="Untitled Diagram")
   diagram.checked_out_by = request.user.username
   diagram.save()
   return redirect('diagram_editor', diagram.uid)

identity_regex = re.compile(r'\\text{id}_\{(?P<subscr>.+)\}|\\text\{id\}_(?P<subscr1>.)|\\text\{id\}')


@login_required
def rename_diagram(request, diagram_id):
   try:
      diagram = get_model_by_uid(Diagram, diagram_id)
      
      if diagram is None:
         raise ObjectDoesNotExist(f'There exists no diagram with uid "{diagram_id}".') 

      if diagram.checked_out_by != request.user.username:
         raise OperationalError(
               f'The diagram with id "{diagram_id}" is already checked out by {diagram.checked_out_by}')                

      new_name = request.body.decode('utf-8')
      new_name = new_name[1:-1]        # Remove weirdly appearing quotes 
      new_name = new_name.replace('\\\\', '\\')
      
      if len(new_name) > MAX_TEXT_LENGTH:
         raise OperationalError(f'Length of string, {len(new_name)} is greater than {MAX_TEXT_LENGTH}')
         
      diagram.name = new_name
      diagram.save()
      
      messages.success(request, f'🤓️ Successfully renamed diagram in the database!')
      response = { 'success' : True }

   except Exception as e:
      messages.error(request, f'😢 {full_qualname(e)}: {str(e)}')
      response = { 'success': False }
      
   return JsonResponse(response)


@login_required
def reassign_category(request, diagram_id):
   try:
      diagram = get_model_by_uid(Diagram, diagram_id)
      
      if diagram is None:
         raise ObjectDoesNotExist(f'There exists no diagram with uid "{diagram_id}".') 

      if diagram.checked_out_by != request.user.username:
         raise OperationalError(
               f'The diagram with id "{diagram_id}" is already checked out by {diagram.checked_out_by}')                

      new_category = request.body.decode('utf-8')
      new_category = new_category[1:-1]      
      new_category = new_category.replace('\\\\', '\\')

      if len(new_category) > MAX_TEXT_LENGTH:
         raise OperationalError(f'Length of string, {len(new_category)} is greater than {MAX_TEXT_LENGTH}')
         
      old_category = diagram.category.get()
      new_category = get_unique(Category, name=new_category)
      diagram.category.reconnect(old_category, new_category)
      diagram.save()
      
      messages.success(request, f'🌌️ Successfully re-assigned the category of this diagram in the database!')
      response = { 'success' : True }

   except Exception as e:
      messages.error(request, f'😢 {full_qualname(e)}: {str(e)}')
      response = { 'success': False }
      
   return JsonResponse(response)


@login_required
def functor_diagram(request, diagram_id=None):
   try:
      notation = request.POST.get('functor_notation')
      codomain_category = request.POST.get('functor_codomain')
      
      if len(notation) > MAX_TEXT_LENGTH:
         raise OperationalError(f'Notation string is too long.')
      
      if len(codomain_category) > MAX_TEXT_LENGTH:
         raise OperationalError(f'Codomain category string is too long.')
   
      diagram = get_model_by_uid(Diagram, uid=diagram_id)
         
      diagram_name = f'Functorial image of diagram "{diagram.name}" under {notation}'
      image_diagram = diagram.copy(name=diagram_name)
      image_diagram.checked_out_by = request.user.username

      for X in image_diagram.all_objects():
         if X.name: 
            parts = []
            
            for name in X.name.split("="):
               parts.append(notation.replace(r'\cdot', name))
               
            X.name = "=".join(parts)
            X.save()
       
         for f in X.all_morphisms():
            if f.name:
               parts = []
               
               for name in f.name.split("="):
                  
                  id_match = identity_regex.match(name)
                  
                  if id_match:
                     subscr1 = id_match.group('subscr1')
                     
                     if subscr1:
                        subscr1 = notation.replace(r'\cdot', subscr1)
                        parts.append(f"\\text{{id}}_{{{subscr1}}}")
                        
                     else:
                        subscr = id_match.group('subscr')
                        
                        if subscr:
                           subscr = notation.replace(r'\cdot', subscr1)                     
                           parts.append(f"\\text{{id}}_{{{subscr}}}")
                     
                  else:
                     parts.append(notation.replace(r'\cdot', name))
                     
                  f.name = "=".join(parts)
                  f.save() 
      
      image_diagram.save()
      
      return redirect('diagram_editor', image_diagram.uid)
      
   except Exception as e:
      messages.error(request, f'{full_qualname(e)}: {str(e)}')
      return redirect('home')
