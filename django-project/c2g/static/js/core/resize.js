function resize_page_contents() {
    var layout_widths = {'l':200, 'r':200, 'm': 800};
    
    var w=window, d=document, e=d.documentElement, g=d.getElementsByTagName('body')[0];
    var viewport_width=w.innerWidth||e.clientWidth||g.clientWidth, viewport_height=w.innerHeight||e.clientHeight||g.clientHeight;
    
    // Resize the viewport div
    var viewport = document.getElementById('viewport');
    viewport.style.width = viewport_width.toString() + 'px';
    viewport.style.height = viewport_height.toString() + 'px';
    
    // Position and resize the content divs
    var l_column = document.getElementById('l_column');
    var m_column = document.getElementById('m_column');
    var r_column = document.getElementById('r_column');
    
    if (l_column.innerHTML.length == 0) l_column = null;
    if (r_column.innerHTML.length == 0) r_column = null;
    
    var total_width = 0;
    if (l_column) total_width += layout_widths['l'] + 10;
    if (r_column) total_width += layout_widths['r'] + 10;
    total_width += layout_widths['m'];
    var left = 0.5*(viewport_width - total_width); if (left < 10) left = 10;
    
    // Left column
    if (l_column) {
        l_column.style.width = layout_widths['l'] + 'px';
        l_column.style.left = left + 'px';
        left += (layout_widths['l'] + 10);
    }
    
    // Middle column
    m_column.style.left = left + 'px';
    m_column.style.width = layout_widths['m'] + 'px';
    left += (layout_widths['m'] + 10);
    
    // Right column
    if (r_column) {
        r_column.style.width = layout_widths['r'] + 'px';
        r_column.style.left = left + 'px';
    }
    
    // resize the topbar
    topbar = document.getElementById('topbar');
    if (viewport_width < total_width + 10) { topbar.style.width = (total_width+10) + 'px';}
    else { topbar.style.width = viewport_width + 'px';}
    
    // Login-Reg Form Canvas
    loginreg_container = document.getElementById('loginreg_container');
    if (loginreg_container) {
        loginreg_container.style.marginLeft = 0.5*(viewport_width - 300) + 'px';
        loginreg_container.style.marginTop = 0.5*(viewport_height - 200) + 'px';
    }
}

$(window).resize(function() {
  resize_page_contents();
});