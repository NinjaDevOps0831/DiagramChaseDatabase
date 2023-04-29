// Edit from Bootstrap Studio

djangoMessagesDiv = null;
djangoMessagesURL = null;

function load_html_from_url(url, elem) {
    elem.load(url)
}

function display_django_messages() {
    messagesDiv = $(djangoMessagesDiv);
    messagesDiv.empty();
    load_html_from_url(djangoMessagesURL, messagesDiv);
}

