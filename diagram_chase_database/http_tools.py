from .settings import MAX_TEXT_LENGTH


def get_posted_text(request, key=None, max_len=MAX_TEXT_LENGTH):
    if request.method != 'POST':
        raise Exception('This setting requires you to use the POST method.')
    
    if key is None:
        key = 'value'
        
    if not key in request.POST:
        raise KeyError('Error, missing POST parameter(s).')
    
    text = request.POST[key]
    text = text.strip()
    
    if len(text) > max_len:
        raise ValueError(f'The text exceeded max length {max_len}')
    
    return text


def get_url_text(request, text, max_len=MAX_TEXT_LENGTH):
    if request.method != 'GET':
        raise Exception('This page requires you to use the GET method.')
    
    if len(text) > max_len:
        raise ValueError(f'The text exceeded max length {max_len}')
    
    return text    
        
        
def get_model_id(request, edit_mode):   
    if edit_mode not in request.session:
        raise Exception(f'You are not currently in {edit_mode} edit mode.')
    
    # The edit item's id is kept in the session which is private.
    # The client doesn't see the id.  This all works as long as
    # only one editor is allowed open at any one time.
    edit_id = request.session[edit_mode]
    
    return edit_id
        