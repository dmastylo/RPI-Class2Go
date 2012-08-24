from django.contrib.sites.models import Site
import markup
import settings

SITE_URL = Site.objects.get_current().domain
STATIC_URL = Site.objects.get_current().domain + settings.STATIC_URL

"""

Helps us develop pages without having to worry about page layout or common page elements such as header, footer ... etc.

Inputs:
---------
* doc_title: The DOM title of the page
* topbar_title: The title to be displayed in the topbar

* head: A dictionary with the following keys:
                'css': List of css to include. Generates one <style> tag per css. The paths provided must be relative to the c2g/static/css directory with no leading slash. The shell and django will append the url prefix
                'scripts': A dictionary of src:type pairs TO include JS files ... etc.  The srcs provided must be relative to the c2g/static/js directory with no leading slash.  The shell and django will append the url prefix
                'meta': A dictionary of meta names-values

* content: A dictionary specifying the layout to use and the content to write on the page.
    * content['layout']: A string restricted to the following values:
        - 'lmr': Left column, main column, and right column
        - 'lm': Left column and main column
        - 'mr': Main column and right column
        - 'm': Main column only
        
    How page width is allocated to columns:
        lmr layout: (This layout is always flushed left)
            width of l-column must be specified explicitly
            width of r-column must be specified explicitly
            m-column can take an optional min_width and max_width parameters. m-column width will be viewport width - (l-column width + r-column width), clipped by min_width (if provided) and max_width (if provided)
            
        lm layout: (This layout is always flushed left)
            width of l-column must be specified explicitly
            m-column can take an optional min_width and max_width parameters. m-column width will be view port width - (l-column width), clipped by min_width (if provided) and max_width (if provided)
    
        mr layout: (This layout is always flushed left)
            m-column can take an optional min_width and max_width parameters. m-column width will be view port width - (l-column width), clipped by min_width (if provided) and max_width (if provided)
        
        m layout:  (This layout may be flushed left or centered, depending on the value of the 'center' parameter (true/false))
            m-column can take an optional min_width and max_width parameters. m-column width will be view port width, clipped by min_width (if provided) and max_width (if provided).
            If max_width is provided and is less than viewport width, a left margin of half the difference will be introduced if 'center' is provided and set to true.
            
    * content['l']: Expected only when content['layout'] is 'lmr' or 'lm'
        * content['l']['width']: The width to allocate to the left column
        * content['l']['content']: The content to display in the left column
        
    * content['r']: Expected only when content['layout'] is 'lmr' or 'mr'
        * content['r']['width']: The width to allocate to the right column
        * content['r']['content']: The content to display in the right column
        
    * content['m']: Expected in all layouts
        * content['m']['min_width']: Optional. The min width to allocate to the main column
        * content['m']['max_width']: Optional. The max width to allocate to the main column
        * content['m']['center']: Optional. Whether to center the main column if its width is less than the viewport width. False if not set
        * content['m']['content']: The content to display in the main column
    
"""

def GenPageHTML(head = {}, topbar = '', content = {}):
    
    # Sanitize inputs
    if not('title' in head):
        head['title'] = 'Class2Go'
    
    if not('scripts' in head):
        head['scripts'] = []
        
    if not('css' in head):
        head['css'] = []
        
    if not('meta' in head):
        head['meta'] = {}
    
    # CSS and JS paths to URLs
    for i, path in enumerate(head['css']):
        head['css'][i] = STATIC_URL + 'css/' + path
    
    temp_dict = {}
    for src,type in head['scripts'].iteritems():
        temp_dict[STATIC_URL + 'js/' + src] = type
    head['scripts'] = temp_dict
    
    # Start of page generation
    page = markup.page()

    ## Head
    page.init(title = head['title'], css = head['css'], script = head['scripts'], metainfo = head['meta'])
    
    ## Body (composed inside-out)
    
    
    # Topbar
    layout_div = markup.page()
    layout_div.add(topbar)
    content_div = markup.page()
    
    
    # Left column
    if ('l' in content['layout']):
        content_div.div(content['l']['content'], class_='layout_left_column', style='width:%s;'%(content['l']['width']))
        
    # Main column
        content_div.div(content['l']['content'], class_='layout_main_column', style='width:%s;'%(content['l']['width']))
    
    # Right column
    if ('r' in content['layout']):
        content_div.div(content['r']['content'], class_='layout_right_column', style='width:%s;'%(content['r']['width']))
        
    layout_div.add(content_div.__str__())
    page.add(layout_div.__str__())
    
    return page.__str__()