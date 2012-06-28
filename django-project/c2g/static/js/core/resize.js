function resize_page_contents() {
	var w=window, d=document, e=d.documentElement, g=d.getElementsByTagName('body')[0];
	var viewport_width=w.innerWidth||e.clientWidth||g.clientWidth, viewport_height=w.innerHeight||e.clientHeight||g.clientHeight;
	
	// Resize the viewport div
	var viewport = document.getElementById('viewport');
	viewport.style.width = viewport_width.toString() + 'px';
	viewport.style.height = viewport_height.toString() + 'px';
	
	// Position and resize the content divs
	var l_column = document.getElementById('c2g_layout_l_column');
	var m_column = document.getElementById('c2g_layout_m_column');
	var r_column = document.getElementById('c2g_layout_r_column');
	
	var total_width = 0;
	if (l_column) total_width += layout_widths['l'] + 10;
	if (r_column) total_width += layout_widths['r'] + 10;
	if (layout_widths['m']) {
		m_width = layout_widths['m'];
	} else {
		m_width = viewport_width - 20 - total_width;
		if (layout_widths['m_min'] && m_width < layout_widths['m_min']) m_width = layout_widths['m_min'];
		if (layout_widths['m_max'] && m_width > layout_widths['m_max']) m_width = layout_widths['m_max'];
	}
	total_width += m_width;
	var left = 0.5*(viewport_width - total_width); if (left < 10) left = 10;
	
	// Left column
	if (l_column) {
		l_column.style.width = layout_widths['l'] + 'px';
		l_column.style.left = left + 'px';
		left += (layout_widths['l'] + 10);
	}
	
	// Middle column
	m_column.style.left = left + 'px';
	m_column.style.width = m_width + 'px';
	left += (m_width + 10);
	
	// Right column
	if (r_column) {
		r_column.style.width = layout_widths['r'] + 'px';
		r_column.style.left = left + 'px';
	}
	
	// resize the topbar
	topbar = document.getElementById('c2g_layout_topbar');
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